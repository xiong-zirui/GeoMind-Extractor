
import json
from pathlib import Path
import logging
from datetime import datetime, timezone
import webbrowser
import tempfile

# Correctly import from sibling directories within src
from config import load_config
from document_processing.pdf_processor import extract_full_text_from_pdf, chunk_text_by_paragraph
# Import the specific extraction functions instead of a non-existent class
from entity_extraction.llm_extractor import extract_metadata, extract_tables, extract_knowledge_graph, configure_agent
from graph_construction.neo4j_loader import Neo4jLoader
from models import Document, DocumentMetadata, Table

# Configure logging to be less verbose
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def create_html_report(document_data, pdf_name):
    """Create an HTML report for visualizing the extraction results."""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Geodata Extraction Results - {pdf_name}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                background: linear-gradient(135deg, #74b9ff, #0984e3);
                color: white;
                padding: 15px;
                border-radius: 5px;
                margin-top: 30px;
            }}
            .metadata-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .metadata-item {{
                background: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }}
            .metadata-label {{
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            .table-container {{
                overflow-x: auto;
                margin: 20px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background: #3498db;
                color: white;
            }}
            .entity {{
                display: inline-block;
                background: #e74c3c;
                color: white;
                padding: 5px 10px;
                margin: 5px;
                border-radius: 15px;
                font-size: 0.9em;
            }}
            .relationship {{
                background: #27ae60;
                color: white;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid #2ecc71;
            }}
            .confidence {{
                float: right;
                background: #f39c12;
                color: white;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 0.8em;
            }}
            .json-container {{
                background: #2c3e50;
                color: #ecf0f1;
                padding: 20px;
                border-radius: 5px;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            .success-badge {{
                background: #27ae60;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                float: right;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 Geodata Extraction Results <span class="success-badge">✅ Success</span></h1>
            <p><strong>Document:</strong> {pdf_name}</p>
            <p><strong>Processed at:</strong> {document_data.processing_timestamp_utc}</p>
            
            <h2>📋 Document Metadata</h2>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="metadata-label">Title</div>
                    <div>{document_data.metadata.title if document_data.metadata else 'N/A'}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Authors</div>
                    <div>{', '.join(document_data.metadata.authors) if document_data.metadata and document_data.metadata.authors else 'N/A'}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Publication Year</div>
                    <div>{document_data.metadata.publication_year if document_data.metadata else 'N/A'}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Keywords</div>
                    <div>{', '.join(document_data.metadata.keywords) if document_data.metadata and document_data.metadata.keywords else 'N/A'}</div>
                </div>
            </div>
            {f'<div class="confidence">Confidence: {document_data.metadata.confidence_score:.2%}</div>' if document_data.metadata else ''}
            
            <h2>📊 Extracted Tables</h2>
            {'<p>No tables found in the document.</p>' if not document_data.extracted_tables else ''}
    """
    
    # Add tables
    for i, table in enumerate(document_data.extracted_tables):
        html_content += f"""
            <h3>Table {i+1}: {table.table_name}</h3>
            <div class="confidence">Confidence: {table.confidence_score:.2%}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            {''.join(f'<th>{col}</th>' for col in table.columns)}
                        </tr>
                    </thead>
                    <tbody>
        """
        for row in table.data[:10]:  # Limit to first 10 rows
            html_content += "<tr>"
            for col in table.columns:
                cell_data = row.row_data.get(col, 'N/A')
                html_content += f"<td>{cell_data}</td>"
            html_content += "</tr>"
        
        if len(table.data) > 10:
            html_content += f"<tr><td colspan='{len(table.columns)}' style='text-align: center; font-style: italic;'>... and {len(table.data) - 10} more rows</td></tr>"
        
        html_content += """
                    </tbody>
                </table>
            </div>
        """
    
    # Add knowledge graph
    html_content += """
            <h2>🕸️ Knowledge Graph</h2>
    """
    
    if document_data.knowledge_graph:
        html_content += f"""
            <div class="confidence">Confidence: {document_data.knowledge_graph.confidence_score:.2%}</div>
            <h3>Entities ({len(document_data.knowledge_graph.entities)})</h3>
            <div>
        """
        for entity in document_data.knowledge_graph.entities:
            html_content += f'<span class="entity">{entity.name} ({entity.type})</span>'
        
        html_content += """
            </div>
            <h3>Relationships ({len(document_data.knowledge_graph.relationships)})</h3>
        """
        for rel in document_data.knowledge_graph.relationships:
            html_content += f'<div class="relationship"><strong>{rel.source}</strong> → <em>{rel.type}</em> → <strong>{rel.target}</strong></div>'
    else:
        html_content += "<p>No knowledge graph could be extracted from the document.</p>"
    
    # Add raw JSON
    html_content += f"""
            <h2>📄 Raw JSON Output</h2>
            <div class="json-container">
                <pre>{json.dumps(document_data.model_dump(), indent=2, ensure_ascii=False)}</pre>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def save_and_open_report(document_data, pdf_name, output_dir):
    """Save the HTML report and open it in the browser."""
    # Create HTML report
    html_content = create_html_report(document_data, pdf_name)
    
    # Save HTML file
    html_file = output_dir / f"{pdf_name.replace('.pdf', '')}_extraction_report.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Open in browser
    webbrowser.open(f'file://{html_file.absolute()}')
    
    return html_file

def process_single_pdf(pdf_path: Path, config: dict):
    """
    Processes a single PDF document by calling individual extraction functions.
    """
    if not pdf_path.is_file():
        logging.error(f"File not found: {pdf_path}")
        return

    logging.info(f"Processing document: {pdf_path.name}")
    full_text = extract_full_text_from_pdf(pdf_path)
    chunks = chunk_text_by_paragraph(full_text)
    
    if not chunks:
        logging.warning(f"No content extracted from {pdf_path.name}. Skipping.")
        return

    # --- Configure the agent ---
    agent = configure_agent(
        agent_type=config["agent_config"]["agent_type"],
        agent_name=config["agent_config"]["agent_name"],
        api_key=config["google_api_key"]
    )

    # 1. Extract Metadata from the first chunk
    logging.info("Extracting metadata...")
    metadata = extract_metadata(agent, chunks[0])
    if not metadata:
        metadata = DocumentMetadata(
            title="Unknown", 
            authors=[], 
            publication_year=None, 
            keywords=[],
            confidence_score=0.0,
            raw_text=chunks[0] if chunks else "No content available"
        )


    # 2. Extract Tables from the full text
    logging.info("Extracting tables...")
    tables = extract_tables(agent, full_text)
    if not tables:
        tables = []

    # 3. Extract Knowledge Graph from the first few chunks
    logging.info("Extracting knowledge graph...")
    # Use first 5 chunks for KG extraction and join them into a single string
    kg_text = " ".join(chunks[:5])
    knowledge_graph = extract_knowledge_graph(agent, kg_text)

    # Consolidate all extracted data into the final Document object
    document_data = Document(
        metadata=metadata,
        extracted_tables=tables,
        knowledge_graph=knowledge_graph,
        source_file=pdf_path.name,
        processing_timestamp_utc=datetime.now(timezone.utc).isoformat(),
        full_text=full_text[:1000] + "..." if len(full_text) > 1000 else full_text  # Truncate if too long
    )
    
    # Create output directory and file paths
    output_dir = Path(config["data_paths"]["processed_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{pdf_path.stem}.json"
    
    # Create and display the report
    print(f"✅ Successfully processed document: {pdf_path.name}")
    html_file = save_and_open_report(document_data, pdf_path.name, output_dir)
    print(f"📊 Extraction report saved to: {html_file}")
    print(f"🌐 Report opened in your default web browser")

    # Also save JSON for programmatic access
    with open(output_path, "w") as f:
        f.write(document_data.model_dump_json(indent=2))
    print(f"💾 JSON data saved to: {output_path}")

    # Optional: Load to Neo4j
    if config.get("neo4j") and config["neo4j"].get("uri") and config["neo4j"].get("password"):
        try:
            neo4j_loader = Neo4jLoader(
                uri=config["neo4j"]["uri"],
                user=config["neo4j"]["user"],
                password=config["neo4j"]["password"],
                database=config["neo4j"]["database"],
            )
            neo4j_loader.load_document(document_data)
            neo4j_loader.close()
            print("🗄️ Successfully loaded knowledge graph to Neo4j.")
        except Exception as e:
            print(f"❌ Failed to load data into Neo4j: {e}")

if __name__ == "__main__":
    print("🚀 Starting Geodata Extraction...")
    config = load_config()
    pdf_file_name = "2008_MATABANE_FE3.pdf"  # Changed to the second PDF
    raw_dir = Path(config["data_paths"]["raw_dir"])
    pdf_path = raw_dir / "theses-WAXI" / pdf_file_name
    print(f"📄 Processing: {pdf_file_name}")
    process_single_pdf(pdf_path, config)
    print("✨ Processing completed!")
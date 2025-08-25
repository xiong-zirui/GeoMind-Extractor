#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Analysis Script - English Version (Complete)
Combines intelligent knowledge synthesis and traditional geological data extraction
Author: Enhanced Analysis System
Date: 2025-08-25
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
import webbrowser

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.debug import (
    IntelligentKnowledgePipeline, LibrarianAgent, MapAnalystAgent, 
    GeochemistAgent, DataAnalystAgent, SynthesizerAgent,
    extract_full_text_from_pdf, chunk_text_by_paragraph,
    configure_agent, extract_metadata, extract_tables, extract_knowledge_graph,
    DocumentMetadata, Document, load_config
)

def comprehensive_analysis(pdf_file_name="2008_MATABANE_FE3.pdf"):
    """Run comprehensive analysis: intelligent analysis + traditional analysis + image extraction"""
    
    # Paths
    pdf_path = Path(f"data/raw/theses-WAXI/{pdf_file_name}")
    config = load_config()
    
    print("🚀 Starting Comprehensive Analysis Mode...")
    print(f"🚀 Beginning comprehensive analysis for: {pdf_file_name}")
    print(f"📄 Processing: {pdf_file_name}")
    
    # Step 1: Run intelligent analysis pipeline
    print("\n" + "="*60)
    print("🧠 Part 1: Intelligent Knowledge Synthesis Analysis")
    print("="*60)
    
    pipeline = IntelligentKnowledgePipeline(mock_mode=False)
    # Manual API key replacement
    pipeline.config['google_api_key'] = "AIzaSyDOxXa1YFX1_sPHHXv85iK_XDoa0VpfYEM"
    
    # Re-initialize agents with correct API key
    pipeline.librarian = LibrarianAgent(pipeline.config)
    pipeline.map_analyst = MapAnalystAgent(pipeline.config)
    pipeline.geochemist = GeochemistAgent(pipeline.config)
    pipeline.data_analyst = DataAnalystAgent(pipeline.config)
    pipeline.synthesizer = SynthesizerAgent(pipeline.config)
    
    intelligent_results = pipeline.process_document(str(pdf_path))
    
    # Step 2: Run traditional analysis workflow
    print("\n" + "="*60)
    print("📊 Part 2: Traditional Geological Data Extraction")
    print("="*60)
    
    traditional_results = run_traditional_analysis(pdf_path, config)
    
    # Step 3: Create comprehensive HTML report
    print("\n" + "="*60)
    print("📋 Part 3: Generate Comprehensive Report")
    print("="*60)
    
    create_comprehensive_report(intelligent_results, traditional_results, pdf_file_name)
    
    print("✨ Comprehensive analysis completed!")

def run_traditional_analysis(pdf_path, config):
    """Run traditional geological data extraction analysis"""
    try:
        if not pdf_path.is_file():
            logging.error(f"File not found: {pdf_path}")
            return None
        
        logging.info(f"Processing document: {pdf_path.name}")
        
        # Extract full text and create chunks
        full_text = extract_full_text_from_pdf(str(pdf_path))
        chunks = chunk_text_by_paragraph(full_text)
        logging.info(f"Split text into {len(chunks)} semantic chunks.")
        
        # Configure agent
        agent = configure_agent(
            config["agent_config"]["agent_type"],
            config["agent_config"]["agent_name"], 
            config["google_api_key"]
        )
        
        # 1. Extract Metadata from the first chunk (usually abstract/introduction)
        metadata = None
        if chunks:
            logging.info("Extracting metadata...")
            metadata = extract_metadata(agent, chunks[0])
        else:
            logging.warning("No chunks found for metadata extraction")
            metadata = DocumentMetadata(
                title="Unknown",
                authors=[],
                keywords=[],
                publication_year=None,
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
        kg_text = " ".join(chunks[:5])
        knowledge_graph = extract_knowledge_graph(agent, kg_text)

        # Consolidate all extracted data into the final Document object
        traditional_results = Document(
            metadata=metadata,
            extracted_tables=tables,
            knowledge_graph=knowledge_graph,
            source_file=pdf_path.name,
            processing_timestamp_utc=datetime.now(timezone.utc).isoformat(),
            full_text=full_text[:1000] + "..." if len(full_text) > 1000 else full_text
        )
        
        return traditional_results
        
    except Exception as e:
        logging.error(f"Traditional analysis failed: {e}")
        return None

def create_comprehensive_report(intelligent_results, traditional_results, pdf_filename):
    """Create comprehensive HTML report combining both analysis results"""
    
    # Extract data from traditional results
    metadata = traditional_results.metadata if traditional_results else None
    tables = traditional_results.extracted_tables if traditional_results else []
    knowledge_graph = traditional_results.knowledge_graph if traditional_results else None
    
    # Get image extraction summary
    pdf_name = pdf_filename.replace('.pdf', '')
    images_dir = f"data/processed/images/{pdf_name}"
    image_summary = get_image_summary(images_dir)
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"data/processed/Comprehensive_Analysis_Report_Complete_{pdf_name}_{timestamp}.html"
    
    # Generate HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Geological Document Analysis Report - {pdf_filename}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .section {{
            background: white;
            margin: 20px 0;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #444;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .section h3 {{
            color: #666;
            margin-top: 25px;
        }}
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .metadata-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metadata-label {{
            font-weight: bold;
            color: #555;
            margin-bottom: 5px;
        }}
        .table-container {{
            overflow-x: auto;
            margin: 15px 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            background: white;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #e3f2fd;
        }}
        .image-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .image-item {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .image-item:hover {{
            transform: translateY(-5px);
        }}
        .image-item img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .image-info {{
            padding: 15px;
        }}
        .image-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .image-details {{
            color: #666;
            font-size: 0.9em;
        }}
        .entity-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }}
        .entity-tag {{
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }}
        .relationship-item {{
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #333;
            color: white;
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Comprehensive Geological Document Analysis Report</h1>
        <p>Document: {pdf_filename}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
    
    # Document basic information
    if metadata:
        html_content += f"""
    <div class="section">
        <h2>📄 Document Basic Information</h2>
        <div class="metadata-grid">
            <div class="metadata-item">
                <div class="metadata-label">Title</div>
                <div>{metadata.title or 'Unknown'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Authors</div>
                <div>{', '.join(metadata.authors) if metadata.authors else 'Unknown'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Keywords</div>
                <div>{', '.join(metadata.keywords) if metadata.keywords else 'None'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Publication Year</div>
                <div>{metadata.publication_year or 'Unknown'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Confidence Score</div>
                <div>{metadata.confidence_score:.2f}</div>
            </div>
        </div>
    </div>
"""
    
    # Image display
    html_content += """
    <div class="section">
        <h2>🖼️ Document Image Extraction</h2>
"""
    
    if image_summary.get('total_images', 0) > 0:
        html_content += f"""
        <p>Successfully extracted <strong>{image_summary.get('total_images', 0)}</strong> images from the document, total size <strong>{image_summary.get('total_size_mb', 0):.2f} MB</strong></p>
        <div class="image-gallery">
"""
        
        # Generate image display based on image metadata
        images_path = Path(images_dir)
        
        if images_path.exists():
            # Read image file list
            image_files = list(images_path.glob("*.jpeg")) + list(images_path.glob("*.jpg")) + list(images_path.glob("*.png"))
            
            # Display first 20 meaningful images (filter out small images)
            meaningful_images = [img for img in sorted(image_files) if img.stat().st_size > 5000][:20]
            
            for img_file in meaningful_images:
                # Create relative path for HTML
                try:
                    rel_path = str(img_file.relative_to(Path.cwd()))
                except ValueError:
                    rel_path = str(img_file.absolute())
                
                # Extract page number from filename
                filename = img_file.name
                page_match = filename.split('_page')[1].split('_')[0] if '_page' in filename else 'Unknown'
                
                html_content += f"""
            <div class="image-item">
                <img src="{rel_path}" alt="Page {page_match} Image" onerror="this.style.display='none'">
                <div class="image-info">
                    <div class="image-title">Page {page_match}</div>
                    <div class="image-details">
                        File: {img_file.name}<br>
                        Size: {img_file.stat().st_size / 1024:.1f} KB
                    </div>
                </div>
            </div>
"""
        
        html_content += """
        </div>
"""
    else:
        html_content += "        <p>No image content found</p>\n"
    
    html_content += "    </div>\n"
    
    # Table data with improved display
    if tables:
        html_content += """
    <div class="section">
        <h2>📊 Extracted Table Data</h2>
"""
        
        for i, table in enumerate(tables, 1):
            html_content += f"""
        <h3>Table {i}</h3>
        <div class="table-container">
            <table>
"""
            
            # Check if table has headers and display them
            if hasattr(table, 'headers') and table.headers:
                html_content += "                <thead><tr>\n"
                for header in table.headers:
                    html_content += f"                    <th>{header}</th>\n"
                html_content += "                </tr></thead>\n"
            
            # Check if table has rows and display them
            if hasattr(table, 'rows') and table.rows:
                html_content += "                <tbody>\n"
                for row in table.rows[:15]:  # Show first 15 rows
                    html_content += "                <tr>\n"
                    if isinstance(row, list):
                        for cell in row:
                            html_content += f"                    <td>{cell}</td>\n"
                    else:
                        html_content += f"                    <td>{row}</td>\n"
                    html_content += "                </tr>\n"
                html_content += "                </tbody>\n"
            elif hasattr(table, 'data') and table.data:
                # Alternative structure check for table.data
                html_content += "                <tbody>\n"
                for row in table.data[:15]:  # Show first 15 rows
                    html_content += "                <tr>\n"
                    if isinstance(row, list):
                        for cell in row:
                            html_content += f"                    <td>{cell}</td>\n"
                    else:
                        html_content += f"                    <td>{row}</td>\n"
                    html_content += "                </tr>\n"
                html_content += "                </tbody>\n"
            else:
                # Fallback: try to display table as string
                table_str = str(table)
                if len(table_str) > 100:
                    html_content += f"                <tbody><tr><td colspan='100%'><pre>{table_str[:500]}...</pre></td></tr></tbody>\n"
                else:
                    html_content += f"                <tbody><tr><td colspan='100%'>{table_str}</td></tr></tbody>\n"
            
            html_content += """
            </table>
        </div>
"""
        
        html_content += "    </div>\n"
    
    # Knowledge graph relationships
    if knowledge_graph and hasattr(knowledge_graph, 'entities'):
        html_content += """
    <div class="section">
        <h2>🕸️ Knowledge Graph Relationships</h2>
        <div class="knowledge-graph">
            <h3>🏷️ Identified Entities</h3>
            <div class="entity-list">
"""
        
        for entity in knowledge_graph.entities[:25]:  # Show first 25 entities
            html_content += f'                <span class="entity-tag">{entity.name} ({entity.type})</span>\n'
        
        html_content += """
            </div>
            
            <h3>🔗 Entity Relationships</h3>
"""
        
        if hasattr(knowledge_graph, 'relationships'):
            for relationship in knowledge_graph.relationships[:15]:  # Show first 15 relationships
                html_content += f"""
            <div class="relationship-item">
                <strong>{relationship.source}</strong> 
                → <em>{relationship.type}</em> → 
                <strong>{relationship.target}</strong>
            </div>
"""
        
        html_content += """
        </div>
    </div>
"""
    
    # Analysis statistics
    html_content += f"""
    <div class="section">
        <h2>📈 Analysis Statistics</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{image_summary.get('total_images', 0)}</div>
                <div class="stat-label">Images Extracted</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(tables)}</div>
                <div class="stat-label">Tables Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(knowledge_graph.entities) if knowledge_graph and hasattr(knowledge_graph, 'entities') else 0}</div>
                <div class="stat-label">Entities Identified</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(knowledge_graph.relationships) if knowledge_graph and hasattr(knowledge_graph, 'relationships') else 0}</div>
                <div class="stat-label">Relationships Found</div>
            </div>
        </div>
    </div>
"""
    
    # Footer
    html_content += f"""
    <div class="footer">
        <p>📊 Comprehensive Analysis Report | Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
        <p>🔬 Geological Document Intelligence System</p>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📋 Comprehensive report generated: {output_filename}")
        
        # Try to open in browser
        try:
            webbrowser.open(f'file://{Path(output_filename).absolute()}')
            print(f"🌐 Report opened in browser: {output_filename}")
        except Exception as e:
            print(f"Note: Could not auto-open browser: {e}")
            
    except Exception as e:
        logging.error(f"Failed to create HTML report: {e}")

def get_image_summary(images_dir):
    """Get summary statistics for extracted images"""
    images_path = Path(images_dir)
    if not images_path.exists():
        return {'total_images': 0, 'total_size_mb': 0}
    
    image_files = list(images_path.glob("*.jpeg")) + list(images_path.glob("*.jpg")) + list(images_path.glob("*.png"))
    total_size = sum(img.stat().st_size for img in image_files)
    
    return {
        'total_images': len(image_files),
        'total_size_mb': total_size / (1024 * 1024)
    }

if __name__ == "__main__":
    # Test with the specified PDF file
    pdf_file = "2008_MATABANE_FE3.pdf"
    comprehensive_analysis(pdf_file)

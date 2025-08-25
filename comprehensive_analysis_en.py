#!/usr/bin/env python# Import necessary modules
from src.debug import (
    IntelligentKnowledgePipeline, 
    LibrarianAgent, 
    MapAnalystAgent, 
    GeochemistAgent, 
    DataAnalystAgent, 
    SynthesizerAgent
)
from src.document_processing.pdf_processor import extract_full_text_from_pdf, chunk_text_by_paragraph
from src.entity_extraction.llm_extractor import extract_metadata, extract_tables, extract_knowledge_graph, configure_agent
from src.config import load_config
from src.models import Documenttf-8 -*-
"""
Comprehensive Analysis Script - English Version
Combines intelligent knowledge synthesis and traditional geological data extraction
Author: Enhanced Analysis System
Date: 2025-08-25
"""

import sys
import os
import logging
from pathlib import Path
import webbrowser
from datetime import datetime

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import necessary modules
from src.debug import (
    extract_text_with_pymupdf,
    extract_images_from_pdf, 
    extract_metadata,
    extract_tables,
    extract_knowledge_graph,
    process_document
)
from src.knowledge_synthesis_pipeline import IntelligentKnowledgePipeline
from src.agents.librarian_agent import LibrarianAgent
from src.agents.map_analyst_agent import MapAnalystAgent
from src.agents.geochemist_agent import GeochemistAgent
from src.agents.data_analyst_agent import DataAnalystAgent
from src.agents.synthesizer_agent import SynthesizerAgent
from src.config import load_config
from src.models import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def comprehensive_analysis(pdf_file):
    """
    Comprehensive analysis combining intelligent knowledge synthesis and traditional geological data extraction
    """
    print("🚀 Starting Comprehensive Analysis Mode...")
    print(f"🚀 Beginning comprehensive analysis for: {pdf_file}")
    pdf_file_name = Path(pdf_file).name
    print(f"📄 Processing: {pdf_file_name}")
    
    print("\n" + "="*60)
    print("🧠 Part 1: Intelligent Knowledge Synthesis Analysis")
    print("="*60)
    
    # Run intelligent pipeline
    intelligent_results = run_intelligent_pipeline(pdf_file)
    
    print("\n" + "="*60)
    print("📊 Part 2: Traditional Geological Data Extraction")
    print("="*60)
    
    # Run traditional analysis
    traditional_results = run_traditional_analysis(pdf_file)
    print(f"✅ Traditional analysis completed: {pdf_file_name}")
    
    print("\n" + "="*60)
    print("📋 Part 3: Generate Comprehensive Report")
    print("="*60)
    
    # Generate comprehensive report
    create_comprehensive_report(intelligent_results, traditional_results, pdf_file_name)
    print("✨ Comprehensive analysis completed!")

def run_intelligent_pipeline(pdf_file):
    """Run intelligent knowledge synthesis pipeline"""
    try:
        pdf_path = Path(pdf_file)
        config = load_config()
        
        # Initialize intelligent pipeline
        pipeline = IntelligentKnowledgePipeline(mock_mode=False)
        # Override API key if needed
        pipeline.config['google_api_key'] = "AIzaSyDOxXa1YFX1_sPHHXv85iK_XDoa0VpfYEM"
        
        # Re-initialize agents with correct API key
        pipeline.librarian = LibrarianAgent(pipeline.config)
        pipeline.map_analyst = MapAnalystAgent(pipeline.config)
        pipeline.geochemist = GeochemistAgent(pipeline.config)
        pipeline.data_analyst = DataAnalystAgent(pipeline.config)
        pipeline.synthesizer = SynthesizerAgent(pipeline.config)
        
        # Process document
        results = pipeline.process_document(str(pdf_path))
        return results
        
    except Exception as e:
        logging.error(f"Intelligent pipeline failed: {e}")
        return None

def run_traditional_analysis(pdf_file):
    """Run traditional geological data extraction analysis"""
    try:
        pdf_path = Path(pdf_file)
        if not pdf_path.is_file():
            logging.error(f"File not found: {pdf_path}")
            return None
        
        logging.info(f"Processing document: {pdf_path.name}")
        
        # Load config and configure agent
        config = load_config()
        agent = configure_agent(
            config["agent_config"]["agent_type"],
            config["agent_config"]["agent_name"], 
            config["google_api_key"]
        )
        
        # Extract full text and create chunks
        full_text = extract_full_text_from_pdf(str(pdf_path))
        chunks = chunk_text_by_paragraph(full_text)
        
        # Extract metadata from first chunk
        metadata = None
        if chunks:
            metadata = extract_metadata(agent, chunks[0])
        
        # Extract tables
        tables = extract_tables(agent, full_text)
        if not tables:
            tables = []
        
        # Extract knowledge graph from first few chunks
        knowledge_graph = None
        if chunks:
            kg_text = " ".join(chunks[:5])
            knowledge_graph = extract_knowledge_graph(agent, kg_text)
        
        # Create Document object
        doc = Document(
            source_file=pdf_path.name,
            processing_timestamp_utc=datetime.utcnow().isoformat(),
            full_text=full_text,
            metadata=metadata,
            extracted_tables=tables,
            knowledge_graph=knowledge_graph,
            image_analysis=[]
        )
        
        return doc
        
    except Exception as e:
        logging.error(f"Traditional analysis failed: {e}")
        return None

def create_comprehensive_report(intelligent_results, traditional_results, pdf_filename):
    """Create comprehensive HTML report combining both analysis results"""
    
    # Extract data from results
    metadata = traditional_results.metadata if traditional_results else None
    tables = traditional_results.extracted_tables if traditional_results else []
    knowledge_graph = traditional_results.knowledge_graph if traditional_results else None
    
    # Get image extraction summary
    pdf_name = pdf_filename.replace('.pdf', '')
    images_dir = f"data/processed/images/{pdf_name}"
    image_summary = get_image_summary(images_dir)
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"data/processed/Comprehensive_Analysis_Report_{pdf_name}_{timestamp}.html"
    
    # Generate HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Analysis Report - {pdf_filename}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(45deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(255,255,255,0.03) 2px,
                rgba(255,255,255,0.03) 4px
            );
            animation: shimmer 20s linear infinite;
        }}
        
        @keyframes shimmer {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
            position: relative;
            z-index: 1;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.1em;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 5px solid #3498db;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        }}
        
        .section h2 {{
            color: #2c3e50;
            margin-top: 0;
            font-size: 1.8em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .metadata-item {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
        }}
        
        .metadata-label {{
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .image-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .image-item {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .image-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .image-item img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            display: block;
        }}
        
        .image-info {{
            padding: 15px;
        }}
        
        .image-title {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .image-details {{
            font-size: 0.85em;
            color: #6c757d;
            line-height: 1.4;
        }}
        
        .table-container {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            margin: 20px 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        th {{
            background: #3498db;
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.8em;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: top;
        }}
        
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        tr:hover {{
            background: #e3f2fd;
        }}
        
        .entity-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }}
        
        .entity-tag {{
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(52, 152, 219, 0.3);
        }}
        
        .relationship-item {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-top: 4px solid #3498db;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: 700;
            color: #3498db;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2980b9);
            border-radius: 3px;
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📊 Comprehensive Analysis Report</h1>
            <p>Geological Document Analysis: {pdf_filename}</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="content">
"""
    
    # Document basic information
    if metadata:
        html_content += f"""
    <!-- Document Basic Information -->
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
                <div>{metadata.confidence_score:.2f}%</div>
            </div>
        </div>
    </div>
"""
    
    # Image display
    html_content += """
    <!-- Extracted Images -->
    <div class="section">
        <h2>🖼️ Document Image Extraction</h2>
"""
    
    if image_summary.get('total_images', 0) > 0:
        html_content += f"""
        <p>Successfully extracted <strong>{image_summary.get('total_images', 0)}</strong> images from the document, total size <strong>{image_summary.get('total_size_mb', 0):.2f} MB</strong></p>
        <div class="image-gallery">
"""
        
        # Generate image display based on image metadata
        images_dir = f"data/processed/images/{pdf_name}"
        images_path = Path(images_dir)
        
        if images_path.exists():
            # Read image file list
            image_files = list(images_path.glob("*.jpeg")) + list(images_path.glob("*.jpg")) + list(images_path.glob("*.png"))
            
            # Display first 20 meaningful images (filter out small images)
            meaningful_images = [img for img in sorted(image_files) if img.stat().st_size > 5000][:20]
            
            for img_file in meaningful_images:
                # Create relative path for HTML - use absolute path
                try:
                    rel_path = str(img_file.relative_to(Path.cwd()))
                except ValueError:
                    # If unable to create relative path, use absolute path
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
    
    # Table data
    if tables:
        html_content += """
    <!-- Extracted Table Data -->
    <div class="section">
        <h2>📊 Extracted Table Data</h2>
"""
        
        for i, table in enumerate(tables, 1):
            html_content += f"""
        <h3>Table {i}</h3>
        <div class="table-container">
            <table>
"""
            
            # Check if table has headers
            if hasattr(table, 'headers') and table.headers:
                html_content += "                <thead><tr>\n"
                for header in table.headers:
                    html_content += f"                    <th>{header}</th>\n"
                html_content += "                </tr></thead>\n"
            
            # Check if table has rows  
            if hasattr(table, 'rows') and table.rows:
                html_content += "                <tbody>\n"
                for row in table.rows[:10]:  # Limit to first 10 rows
                    html_content += "                <tr>\n"
                    for cell in row:
                        html_content += f"                    <td>{cell}</td>\n"
                    html_content += "                </tr>\n"
                html_content += "                </tbody>\n"
            elif hasattr(table, 'data') and table.data:
                # Alternative structure check
                html_content += "                <tbody>\n"
                for row in table.data[:10]:  # Limit to first 10 rows
                    html_content += "                <tr>\n"
                    if isinstance(row, list):
                        for cell in row:
                            html_content += f"                    <td>{cell}</td>\n"
                    else:
                        html_content += f"                    <td>{row}</td>\n"
                    html_content += "                </tr>\n"
                html_content += "                </tbody>\n"
            else:
                # If no standard structure, try to display table content
                html_content += f"                <tbody><tr><td colspan='100%'>Table content: {str(table)[:500]}...</td></tr></tbody>\n"
            
            html_content += """
            </table>
        </div>
"""
        
        html_content += "    </div>\n"
    
    # Knowledge graph
    if knowledge_graph and hasattr(knowledge_graph, 'entities'):
        html_content += """
    <!-- Knowledge Graph Relationships -->
    <div class="section">
        <h2>🕸️ Knowledge Graph Relationships</h2>
        <div class="knowledge-graph">
            <h3>🏷️ Identified Entities</h3>
            <div class="entity-list">
"""
        
        for entity in knowledge_graph.entities[:20]:  # Limit to first 20 entities
            html_content += f'                <span class="entity-tag">{entity.name} ({entity.type})</span>\n'
        
        html_content += """
            </div>
            
            <h3>🔗 Entity Relationships</h3>
"""
        
        if hasattr(knowledge_graph, 'relationships'):
            for relationship in knowledge_graph.relationships[:10]:  # Limit to first 10 relationships
                html_content += f"""
            <div class="relationship-item">
                <strong>{relationship.source}</strong> 
                → <em>{relationship.type}</em> → 
                <strong>{relationship.target}</strong>
                {f'<br><small>Confidence: {relationship.confidence}</small>' if hasattr(relationship, 'confidence') else ''}
            </div>
"""
        
        html_content += """
        </div>
    </div>
"""
    
    # Analysis statistics
    html_content += f"""
    <!-- Analysis Statistics -->
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
        </div>
        
        <footer class="footer">
            <p>📊 Comprehensive Analysis Report | Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
            <p>🔬 Geological Document Intelligence System</p>
        </footer>
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
    pdf_file = "data/raw/theses-WAXI/2008_MATABANE_FE3.pdf"
    
    if not Path(pdf_file).exists():
        print(f"❌ Error: File not found: {pdf_file}")
        sys.exit(1)
    
    comprehensive_analysis(pdf_file)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Analysis Script - English Version (Final)
Uses cached data to generate complete report with all content sections
Author: Enhanced Analysis System
Date: 2025-08-25
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
import webbrowser

def comprehensive_analysis_final(pdf_file_name="2008_MATABANE_FE3.pdf"):
    """Generate final comprehensive analysis report using cached data"""
    
    print("🚀 Starting Final Comprehensive Analysis...")
    print(f"📄 Processing: {pdf_file_name}")
    
    # Load cached traditional analysis data
    pdf_name = pdf_file_name.replace('.pdf', '')
    cached_data_file = f"data/processed/{pdf_name}.json"
    
    traditional_data = None
    if Path(cached_data_file).exists():
        with open(cached_data_file, 'r', encoding='utf-8') as f:
            traditional_data = json.load(f)
        print("✅ Loaded cached traditional analysis data")
    else:
        print("❌ No cached data found")
        return
    
    # Get image extraction summary
    images_dir = f"data/processed/images/{pdf_name}"
    image_summary = get_image_summary(images_dir)
    print(f"✅ Found {image_summary.get('total_images', 0)} images")
    
    # Generate comprehensive report
    print("\n📋 Generating comprehensive HTML report...")
    create_final_comprehensive_report(traditional_data, image_summary, pdf_file_name)
    
    print("✨ Final comprehensive analysis completed!")

def create_final_comprehensive_report(traditional_data, image_summary, pdf_filename):
    """Create comprehensive HTML report with all content sections"""
    
    # Extract data from traditional results
    metadata = traditional_data.get('metadata', {})
    tables = traditional_data.get('extracted_tables', [])
    knowledge_graph = traditional_data.get('knowledge_graph', {})
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_name = pdf_filename.replace('.pdf', '')
    output_filename = f"data/processed/Final_Comprehensive_Analysis_Report_{pdf_name}_{timestamp}.html"
    
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
            font-size: 1.8em;
        }}
        .section h3 {{
            color: #666;
            margin-top: 25px;
            font-size: 1.4em;
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
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}
        .metadata-value {{
            color: #333;
            font-size: 1.1em;
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
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
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
            background: linear-gradient(45deg, #667eea, #5a67d8);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
        }}
        .relationship-item {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #333;
            color: white;
            border-radius: 10px;
        }}
        .table-header {{
            background: #667eea;
            color: white;
            padding: 10px 15px;
            border-radius: 5px 5px 0 0;
            font-weight: bold;
            margin-bottom: 0;
        }}
        .highlight {{
            background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Comprehensive Geological Document Analysis Report</h1>
        <p><strong>Document:</strong> {pdf_filename}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="highlight">
            Complete analysis including document metadata, extracted tables, knowledge graph relationships, and image gallery
        </div>
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
                <div class="metadata-value">{metadata.get('title', 'Unknown')}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Author(s)</div>
                <div class="metadata-value">{', '.join(metadata.get('authors', [])) if metadata.get('authors') else 'Unknown'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Keywords</div>
                <div class="metadata-value">{', '.join(metadata.get('keywords', [])) if metadata.get('keywords') else 'None'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Publication Year</div>
                <div class="metadata-value">{metadata.get('publication_year', 'Unknown')}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Confidence Score</div>
                <div class="metadata-value">{metadata.get('confidence_score', 0):.2f}</div>
            </div>
        </div>
    </div>
"""
    
    # Table data with improved display
    if tables:
        html_content += """
    <div class="section">
        <h2>📊 Extracted Table Data</h2>
        <p>The following tables were automatically extracted and structured from the geological document:</p>
"""
        
        for i, table in enumerate(tables, 1):
            table_name = table.get('table_name', f'Table {i}')
            html_content += f"""
        <h3 class="table-header">{table_name}</h3>
        <div class="table-container">
            <table>
"""
            
            # Display table columns as headers
            columns = table.get('columns', [])
            if columns:
                html_content += "                <thead><tr>\n"
                for col in columns:
                    html_content += f"                    <th>{col if col else 'Column'}</th>\n"
                html_content += "                </tr></thead>\n"
            
            # Display table data
            data = table.get('data', [])
            if data:
                html_content += "                <tbody>\n"
                for row_item in data[:20]:  # Show first 20 rows
                    html_content += "                <tr>\n"
                    if isinstance(row_item, dict) and 'row_data' in row_item:
                        row_data = row_item['row_data']
                        for col in columns:
                            cell_value = row_data.get(col, '')
                            html_content += f"                    <td>{cell_value}</td>\n"
                    else:
                        # Fallback for other data structures
                        html_content += f"                    <td>{str(row_item)}</td>\n"
                    html_content += "                </tr>\n"
                html_content += "                </tbody>\n"
            
            html_content += """
            </table>
        </div>
        <p><small><em>Confidence Score: {:.2f}</em></small></p>
""".format(table.get('confidence_score', 0))
        
        html_content += "    </div>\n"
    
    # Knowledge graph relationships
    kg_entities = knowledge_graph.get('entities', [])
    kg_relationships = knowledge_graph.get('relationships', [])
    
    if kg_entities or kg_relationships:
        html_content += """
    <div class="section">
        <h2>🕸️ Knowledge Graph Relationships</h2>
        <p>Automatically identified geological entities and their relationships from the document text:</p>
"""
        
        if kg_entities:
            html_content += """
        <h3>🏷️ Identified Entities</h3>
        <div class="entity-list">
"""
            for entity in kg_entities[:30]:  # Show first 30 entities
                entity_name = entity.get('name', 'Unknown')
                entity_type = entity.get('type', 'Unknown')
                html_content += f'            <span class="entity-tag">{entity_name} ({entity_type})</span>\n'
            
            html_content += """
        </div>
"""
        
        if kg_relationships:
            html_content += """
        <h3>🔗 Entity Relationships</h3>
"""
            for relationship in kg_relationships[:20]:  # Show first 20 relationships
                source = relationship.get('source', 'Unknown')
                target = relationship.get('target', 'Unknown')
                rel_type = relationship.get('type', 'RELATED_TO')
                html_content += f"""
        <div class="relationship-item">
            <strong>{source}</strong> 
            → <em>{rel_type}</em> → 
            <strong>{target}</strong>
        </div>
"""
        
        html_content += "    </div>\n"
    
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
        
        # Generate image display
        pdf_name = pdf_filename.replace('.pdf', '')
        images_dir = f"data/processed/images/{pdf_name}"
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
                <div class="stat-number">{len(kg_entities)}</div>
                <div class="stat-label">Entities Identified</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(kg_relationships)}</div>
                <div class="stat-label">Relationships Found</div>
            </div>
        </div>
    </div>
"""
    
    # Footer
    html_content += f"""
    <div class="footer">
        <p>📊 <strong>Comprehensive Analysis Report</strong> | Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
        <p>🔬 Geological Document Intelligence System</p>
        <p>🎯 Complete extraction of metadata, tables, entities, relationships, and images</p>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📋 Final comprehensive report generated: {output_filename}")
        
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
    # Generate final comprehensive report
    pdf_file = "2008_MATABANE_FE3.pdf"
    comprehensive_analysis_final(pdf_file)

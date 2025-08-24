import json
from pathlib import Path
import logging
from datetime import datetime, timezone
import webbrowser
from typing import Dict, List, Any
from collections import defaultdict

# Import our modules
from config import load_config
from document_processing.pdf_processor import extract_full_text_from_pdf, chunk_text_by_paragraph
from entity_extraction.llm_extractor import extract_metadata, extract_tables, extract_knowledge_graph, configure_agent
from models import Document, DocumentMetadata, Table

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

class GeodataAnalyzer:
    """
    Enhanced analyzer that categorizes, classifies and stores geological information
    with logical analysis capabilities.
    """
    
    def __init__(self, config):
        self.config = config
        self.agent = configure_agent(
            agent_type=config["agent_config"]["agent_type"],
            agent_name=config["agent_config"]["agent_name"],
            api_key=config["google_api_key"]
        )
        self.output_dir = Path(config["data_paths"]["processed_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize category storage
        self.categories = {
            'geological_formations': [],
            'minerals_and_rocks': [],
            'geographic_locations': [],
            'geological_processes': [],
            'temporal_data': [],
            'analytical_methods': [],
            'economic_geology': [],
            'structural_features': []
        }
        
    def categorize_entities(self, knowledge_graph):
        """Categorize extracted entities into geological categories"""
        if not knowledge_graph or not knowledge_graph.entities:
            return self.categories
            
        entity_categories = defaultdict(list)
        
        for entity in knowledge_graph.entities:
            entity_type = entity.type.upper()
            entity_name = entity.name.lower()
            entity_display_name = entity.name
            
            # Enhanced categorization logic based on entity types and names
            if entity_type in ['LOCATION', 'PLACE', 'GEOGRAPHIC']:
                self.categories['geographic_locations'].append({
                    'name': entity_display_name,
                    'type': entity_type,
                    'category': 'geographic_locations'
                })
            elif entity_type in ['MINERAL', 'ROCK', 'LITHOLOGY'] or any(keyword in entity_name for keyword in ['gold', 'arsenopyrite', 'pyrite', 'quartz', 'granite', 'basalt']):
                self.categories['minerals_and_rocks'].append({
                    'name': entity_display_name,
                    'type': entity_type,
                    'category': 'minerals_and_rocks'
                })
            elif (entity_type in ['FORMATION', 'UNIT', 'GROUP', 'MEMBER', 'GEOLOGICAL_FORMATION'] or 
                  any(keyword in entity_name for keyword in ['facies', 'unit', 'formation', 'profile', 'pluton', 'complex'])):
                self.categories['geological_formations'].append({
                    'name': entity_display_name,
                    'type': entity_type,
                    'category': 'geological_formations'
                })
            elif entity_type in ['PROCESS', 'EVENT'] or any(keyword in entity_name for keyword in ['weathering', 'erosion', 'deformation', 'metamorphism']):
                self.categories['geological_processes'].append({
                    'name': entity_display_name,
                    'type': entity_type,
                    'category': 'geological_processes'
                })
            elif entity_type in ['AGE', 'TIME', 'PERIOD', 'ERA'] or any(keyword in entity_name for keyword in ['ma', 'mya', 'age', 'period', 'era']):
                self.categories['temporal_data'].append({
                    'name': entity_display_name,
                    'type': entity_type,
                    'category': 'temporal_data'
                })
            elif entity_type in ['METHOD', 'TECHNIQUE', 'ANALYSIS'] or any(keyword in entity_name for keyword in ['analysis', 'xrd', 'sem', 'assay', 'drilling']):
                self.categories['analytical_methods'].append({
                    'name': entity_display_name,
                    'type': entity_type,
                    'category': 'analytical_methods'
                })
            elif (entity_type in ['DEPOSIT', 'ORE', 'GOLD', 'COPPER', 'ZINC'] or 
                  any(keyword in entity_name for keyword in ['deposit', 'ore', 'mining', 'exploration', 'resource'])):
                self.categories['economic_geology'].append({
                    'name': entity_display_name,
                    'type': entity_type,
                    'category': 'economic_geology'
                })
            elif (entity_type in ['FAULT', 'FOLD', 'SHEAR', 'STRUCTURE', 'GEOLOGICAL_STRUCTURE'] or 
                  any(keyword in entity_name for keyword in ['fault', 'fold', 'shear', 'dyke', 'dike', 'vein', 'fracture', 'joint', 'channel'])):
                self.categories['structural_features'].append({
                    'name': entity_display_name,
                    'type': entity_type,
                    'category': 'structural_features'
                })
            else:
                # Default categorization based on context
                if 'gold' in entity_name or 'ore' in entity_name:
                    self.categories['economic_geology'].append({
                        'name': entity_display_name,
                        'type': entity_type,
                        'category': 'economic_geology'
                    })
                else:
                    # Add to geological formations as default for geological entities
                    self.categories['geological_formations'].append({
                        'name': entity_display_name,
                        'type': entity_type,
                        'category': 'geological_formations'
                    })
                
        return self.categories
    
    def analyze_relationships(self, knowledge_graph):
        """Analyze relationships between entities to derive logical insights"""
        if not knowledge_graph or not knowledge_graph.relationships:
            return {}
            
        relationship_analysis = {
            'spatial_relationships': [],
            'temporal_relationships': [],
            'compositional_relationships': [],
            'genetic_relationships': []
        }
        
        for rel in knowledge_graph.relationships:
            rel_type = rel.type.upper()
            
            if rel_type in ['LOCATED_IN', 'CONTAINS', 'NEAR', 'ADJACENT']:
                relationship_analysis['spatial_relationships'].append({
                    'source': rel.source,
                    'target': rel.target,
                    'relationship': rel.type,
                    'type': 'spatial'
                })
            elif rel_type in ['BEFORE', 'AFTER', 'DURING', 'CONTEMPORANEOUS']:
                relationship_analysis['temporal_relationships'].append({
                    'source': rel.source,
                    'target': rel.target,
                    'relationship': rel.type,
                    'type': 'temporal'
                })
            elif rel_type in ['COMPOSED_OF', 'CONTAINS_MINERAL', 'INCLUDES']:
                relationship_analysis['compositional_relationships'].append({
                    'source': rel.source,
                    'target': rel.target,
                    'relationship': rel.type,
                    'type': 'compositional'
                })
            elif rel_type in ['CAUSED_BY', 'RESULTS_IN', 'ASSOCIATED_WITH']:
                relationship_analysis['genetic_relationships'].append({
                    'source': rel.source,
                    'target': rel.target,
                    'relationship': rel.type,
                    'type': 'genetic'
                })
                
        return relationship_analysis
    
    def generate_insights(self, document_data, categories, relationships):
        """Generate logical insights from the extracted and categorized data"""
        insights = {
            'summary': {},
            'key_findings': [],
            'geological_context': {},
            'recommendations': []
        }
        
        # Summary statistics
        insights['summary'] = {
            'total_entities': len(document_data.knowledge_graph.entities) if document_data.knowledge_graph else 0,
            'total_relationships': len(document_data.knowledge_graph.relationships) if document_data.knowledge_graph else 0,
            'categories_found': {k: len(v) for k, v in categories.items() if v},
            'relationship_types': {k: len(v) for k, v in relationships.items() if v}
        }
        
        # Key findings based on entity density
        for category, entities in categories.items():
            if len(entities) >= 3:  # Significant presence
                insights['key_findings'].append(f"Significant focus on {category.replace('_', ' ')}: {len(entities)} entities identified")
        
        # Geological context
        if categories['geographic_locations']:
            locations = [e['name'] for e in categories['geographic_locations']]
            insights['geological_context']['study_area'] = locations
            
        if categories['temporal_data']:
            ages = [e['name'] for e in categories['temporal_data']]
            insights['geological_context']['time_periods'] = ages
            
        # Recommendations for further analysis
        if len(categories['economic_geology']) > 0:
            insights['recommendations'].append("Economic potential identified - recommend detailed resource assessment")
            
        if len(relationships['spatial_relationships']) > 5:
            insights['recommendations'].append("Complex spatial relationships detected - recommend GIS analysis")
            
        return insights
    
    def process_document(self, pdf_path: Path):
        """Enhanced document processing with categorization and analysis"""
        print(f"🔍 Starting enhanced analysis of: {pdf_path.name}")
        
        if not pdf_path.is_file():
            print(f"❌ File not found: {pdf_path}")
            return None
            
        # Step 1: Extract text and chunk
        print("📄 Extracting text...")
        full_text = extract_full_text_from_pdf(pdf_path)
        chunks = chunk_text_by_paragraph(full_text)
        
        if not chunks:
            print("❌ No content extracted. Skipping.")
            return None
            
        print(f"✅ Extracted {len(chunks)} semantic chunks")
        
        # Step 2: Extract structured data
        print("🧠 Extracting metadata...")
        metadata = extract_metadata(self.agent, chunks[0])
        if not metadata:
            metadata = DocumentMetadata(
                title="Unknown", 
                authors=[], 
                publication_year=None, 
                keywords=[],
                confidence_score=0.0,
                raw_text=chunks[0] if chunks else "No content available"
            )
            
        print("📊 Extracting tables...")
        tables = extract_tables(self.agent, full_text)
        if not tables:
            tables = []
            
        print("🕸️ Extracting knowledge graph...")
        kg_text = " ".join(chunks[:5])
        knowledge_graph = extract_knowledge_graph(self.agent, kg_text)
        
        # Step 3: Create document object
        document_data = Document(
            metadata=metadata,
            extracted_tables=tables,
            knowledge_graph=knowledge_graph,
            source_file=pdf_path.name,
            processing_timestamp_utc=datetime.now(timezone.utc).isoformat(),
            full_text=full_text[:2000] + "..." if len(full_text) > 2000 else full_text
        )
        
        # Step 4: Enhanced analysis
        print("🔬 Performing categorical analysis...")
        categories = self.categorize_entities(knowledge_graph)
        
        print("🔗 Analyzing relationships...")
        relationships = self.analyze_relationships(knowledge_graph)
        
        print("💡 Generating insights...")
        insights = self.generate_insights(document_data, categories, relationships)
        
        # Step 5: Save categorized data
        analysis_results = {
            'document_info': {
                'filename': pdf_path.name,
                'processing_time': datetime.now(timezone.utc).isoformat(),
                'confidence_scores': {
                    'metadata': metadata.confidence_score if metadata else 0,
                    'knowledge_graph': knowledge_graph.confidence_score if knowledge_graph else 0
                }
            },
            'raw_extraction': document_data.model_dump(),
            'categorized_entities': categories,
            'relationship_analysis': relationships,
            'insights': insights
        }
        
        # Save to different formats for different use cases
        base_name = pdf_path.stem
        
        # 1. Complete analysis JSON
        analysis_file = self.output_dir / f"{base_name}_complete_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            
        # 2. Categories-only JSON (for quick reference)
        categories_file = self.output_dir / f"{base_name}_categories.json"
        with open(categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
            
        # 3. Insights summary
        insights_file = self.output_dir / f"{base_name}_insights.json"
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
            
        # 4. Generate HTML dashboard
        self.generate_dashboard(analysis_results, base_name)
        
        print(f"💾 Analysis saved to:")
        print(f"  📋 Complete: {analysis_file}")
        print(f"  🏷️  Categories: {categories_file}")
        print(f"  💡 Insights: {insights_file}")
        
        return analysis_results
    
    def generate_dashboard(self, analysis_results, base_name):
        """Generate interactive HTML dashboard"""
        dashboard_path = self.output_dir / f"{base_name}_dashboard.html"
        
        # Create complete dashboard HTML with embedded data
        dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Geodata Analysis: {analysis_results['document_info']['filename']}</title>
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --light-bg: #ecf0f1;
            --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--primary-color);
            background-color: var(--light-bg);
        }}

        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
        }}

        .header h1 {{
            color: var(--primary-color);
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: var(--secondary-color);
            font-size: 1.2em;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .stat-label {{
            color: #666;
            font-weight: 500;
        }}

        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        .categories-section, .relationships-section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
        }}

        .section-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: var(--primary-color);
            border-bottom: 3px solid var(--secondary-color);
            padding-bottom: 10px;
        }}

        .category-item {{
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid var(--secondary-color);
        }}

        .category-title {{
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 8px;
        }}

        .entity-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .entity-tag {{
            background: var(--secondary-color);
            color: white;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.85em;
        }}

        .relationship-item {{
            margin-bottom: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
            font-size: 0.9em;
        }}

        .insights-section {{
            grid-column: 1 / -1;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
        }}

        .findings-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}

        .finding-card {{
            background: #e8f4f8;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--success-color);
        }}

        .recommendation-card {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--warning-color);
        }}

        .context-item {{
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 6px;
            border-left: 3px solid var(--secondary-color);
        }}

        .no-data {{
            text-align: center;
            color: #999;
            font-style: italic;
            padding: 20px;
        }}

        @media (max-width: 768px) {{
            .content-grid {{
                grid-template-columns: 1fr;
            }}
            
            .findings-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🌍 Geodata Analysis: {analysis_results['document_info']['filename']}</h1>
            <div class="subtitle">Intelligent Categorization & Analysis Results</div>
        </div>

        <div class="stats-grid" id="statsGrid">
            <!-- Stats will be populated by JavaScript -->
        </div>

        <div class="content-grid">
            <div class="categories-section">
                <h2 class="section-title">📁 Entity Categories</h2>
                <div id="categoriesContainer">
                    <!-- Categories will be populated by JavaScript -->
                </div>
            </div>

            <div class="relationships-section">
                <h2 class="section-title">🔗 Relationship Analysis</h2>
                <div id="relationshipsContainer">
                    <!-- Relationships will be populated by JavaScript -->
                </div>
            </div>

            <div class="insights-section">
                <h2 class="section-title">💡 Insights & Analysis</h2>
                <div class="findings-grid">
                    <div>
                        <h3>🔍 Key Findings</h3>
                        <div id="findingsContainer">
                            <!-- Findings will be populated by JavaScript -->
                        </div>
                    </div>
                    <div>
                        <h3>💡 Recommendations</h3>
                        <div id="recommendationsContainer">
                            <!-- Recommendations will be populated by JavaScript -->
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h3>🗺️ Geological Context</h3>
                    <div id="contextContainer">
                        <!-- Context will be populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Analysis data embedded directly
        const ANALYSIS_DATA = {json.dumps(analysis_results, indent=8, ensure_ascii=False)};
        
        function loadAnalysisData() {{
            displayStats(ANALYSIS_DATA.insights.summary);
            displayCategories(ANALYSIS_DATA.categorized_entities);
            displayRelationships(ANALYSIS_DATA.relationship_analysis);
            displayInsights(ANALYSIS_DATA.insights);
        }}

        function displayStats(summary) {{
            const statsGrid = document.getElementById('statsGrid');
            const stats = [
                {{ label: 'Total Entities', value: summary.total_entities, color: 'var(--secondary-color)' }},
                {{ label: 'Relationships', value: summary.total_relationships, color: 'var(--success-color)' }},
                {{ label: 'Categories', value: Object.keys(summary.categories_found).length, color: 'var(--warning-color)' }},
                {{ label: 'Relationship Types', value: Object.keys(summary.relationship_types).length, color: 'var(--danger-color)' }}
            ];

            statsGrid.innerHTML = stats.map(stat => `
                <div class="stat-card">
                    <div class="stat-number" style="color: ${{stat.color}}">${{stat.value}}</div>
                    <div class="stat-label">${{stat.label}}</div>
                </div>
            `).join('');
        }}

        function displayCategories(categories) {{
            const container = document.getElementById('categoriesContainer');
            
            if (!categories || Object.keys(categories).length === 0) {{
                container.innerHTML = '<div class="no-data">No categorized entities found</div>';
                return;
            }}

            const categoryNames = {{
                'geological_formations': '🏔️ Geological Formations',
                'minerals_and_rocks': '💎 Minerals & Rocks',
                'geographic_locations': '📍 Geographic Locations',
                'geological_processes': '🌋 Geological Processes',
                'temporal_data': '⏰ Temporal Data',
                'analytical_methods': '🔬 Analytical Methods',
                'economic_geology': '💰 Economic Geology',
                'structural_features': '🗻 Structural Features'
            }};

            container.innerHTML = Object.entries(categories)
                .filter(([key, entities]) => entities && entities.length > 0)
                .map(([key, entities]) => `
                    <div class="category-item">
                        <div class="category-title">${{categoryNames[key] || key}}</div>
                        <div class="entity-list">
                            ${{entities.map(entity => `<span class="entity-tag">${{entity.name}}</span>`).join('')}}
                        </div>
                    </div>
                `).join('') || '<div class="no-data">No categorized entities found</div>';
        }}

        function displayRelationships(relationships) {{
            const container = document.getElementById('relationshipsContainer');
            
            if (!relationships || Object.keys(relationships).length === 0) {{
                container.innerHTML = '<div class="no-data">No relationships found</div>';
                return;
            }}

            const relationshipTypes = {{
                'spatial_relationships': '🗺️ Spatial',
                'temporal_relationships': '⏰ Temporal',
                'compositional_relationships': '🧪 Compositional',
                'genetic_relationships': '🔗 Genetic'
            }};

            container.innerHTML = Object.entries(relationships)
                .filter(([key, rels]) => rels && rels.length > 0)
                .map(([key, rels]) => `
                    <div style="margin-bottom: 15px;">
                        <strong>${{relationshipTypes[key] || key}} (${{rels.length}})</strong>
                        ${{rels.slice(0, 3).map(rel => `
                            <div class="relationship-item">
                                ${{rel.source}} → ${{rel.relationship}} → ${{rel.target}}
                            </div>
                        `).join('')}}
                        ${{rels.length > 3 ? `<div class="relationship-item" style="text-align: center; font-style: italic;">...and ${{rels.length - 3}} more</div>` : ''}}
                    </div>
                `).join('') || '<div class="no-data">No relationships found</div>';
        }}

        function displayInsights(insights) {{
            // Key Findings
            const findingsContainer = document.getElementById('findingsContainer');
            if (insights.key_findings && insights.key_findings.length > 0) {{
                findingsContainer.innerHTML = insights.key_findings.map(finding => `
                    <div class="finding-card">${{finding}}</div>
                `).join('');
            }} else {{
                findingsContainer.innerHTML = '<div class="no-data">No key findings available</div>';
            }}

            // Recommendations
            const recommendationsContainer = document.getElementById('recommendationsContainer');
            if (insights.recommendations && insights.recommendations.length > 0) {{
                recommendationsContainer.innerHTML = insights.recommendations.map(rec => `
                    <div class="recommendation-card">${{rec}}</div>
                `).join('');
            }} else {{
                recommendationsContainer.innerHTML = '<div class="no-data">No recommendations available</div>';
            }}

            // Geological Context
            const contextContainer = document.getElementById('contextContainer');
            if (insights.geological_context && Object.keys(insights.geological_context).length > 0) {{
                contextContainer.innerHTML = Object.entries(insights.geological_context).map(([key, value]) => `
                    <div class="context-item">
                        <strong>${{key.replace('_', ' ').toUpperCase()}}:</strong> ${{Array.isArray(value) ? value.join(', ') : value}}
                    </div>
                `).join('');
            }} else {{
                contextContainer.innerHTML = '<div class="no-data">No geological context available</div>';
            }}
        }}

        // Load data when page loads
        window.addEventListener('DOMContentLoaded', loadAnalysisData);
    </script>
</body>
</html>"""
        
        # Write dashboard
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        print(f"  📊 Dashboard: {dashboard_path}")
        
        # Open dashboard in browser
        webbrowser.open(f'file://{dashboard_path.absolute()}')
        print(f"  🌐 Dashboard opened in browser")

def main():
    """Main function to run enhanced analysis"""
    print("🚀 Starting Enhanced Geodata Analysis...")
    
    config = load_config()
    analyzer = GeodataAnalyzer(config)
    
    # Process current document
    pdf_file_name = "2008_MATABANE_FE3.pdf"
    raw_dir = Path(config["data_paths"]["raw_dir"])
    pdf_path = raw_dir / "theses-WAXI" / pdf_file_name
    
    results = analyzer.process_document(pdf_path)
    
    if results:
        print("\n📊 Analysis Summary:")
        summary = results['insights']['summary']
        print(f"  🔢 Total entities: {summary['total_entities']}")
        print(f"  🔗 Total relationships: {summary['total_relationships']}")
        print(f"  📁 Categories with data: {len([k for k, v in summary['categories_found'].items() if v > 0])}")
        
        if results['insights']['key_findings']:
            print("\n🔍 Key Findings:")
            for finding in results['insights']['key_findings']:
                print(f"  • {finding}")
                
        if results['insights']['recommendations']:
            print("\n💡 Recommendations:")
            for rec in results['insights']['recommendations']:
                print(f"  • {rec}")
    
    print("\n✨ Enhanced analysis completed!")

if __name__ == "__main__":
    main()

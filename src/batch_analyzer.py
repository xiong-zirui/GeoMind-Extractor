import json
from pathlib import Path
import logging
from datetime import datetime, timezone
import webbrowser
from typing import Dict, List, Any
import pandas as pd

# Import our enhanced analyzer
from enhanced_analyzer import GeodataAnalyzer
from config import load_config

class BatchGeodataAnalyzer:
    """
    Batch processor for multiple PDF documents with comparative analysis
    """
    
    def __init__(self, config):
        self.config = config
        self.analyzer = GeodataAnalyzer(config)
        self.output_dir = Path(config["data_paths"]["processed_dir"])
        self.batch_results = []
        
    def process_batch(self, pdf_directory: Path, file_pattern="*.pdf", max_files=None):
        """Process multiple PDF files and generate comparative analysis"""
        print(f"🔄 Starting batch analysis of PDFs in: {pdf_directory}")
        
        pdf_files = list(pdf_directory.glob(file_pattern))
        if max_files:
            pdf_files = pdf_files[:max_files]
            
        print(f"📁 Found {len(pdf_files)} PDF files to process")
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n{'='*60}")
            print(f"📄 Processing file {i}/{len(pdf_files)}: {pdf_path.name}")
            print(f"{'='*60}")
            
            try:
                results = self.analyzer.process_document(pdf_path)
                if results:
                    self.batch_results.append({
                        'filename': pdf_path.name,
                        'success': True,
                        'results': results
                    })
                else:
                    self.batch_results.append({
                        'filename': pdf_path.name,
                        'success': False,
                        'error': 'No results returned'
                    })
            except Exception as e:
                print(f"❌ Error processing {pdf_path.name}: {str(e)}")
                self.batch_results.append({
                    'filename': pdf_path.name,
                    'success': False,
                    'error': str(e)
                })
        
        # Generate comparative analysis
        print(f"\n{'='*60}")
        print("🔍 Generating Comparative Analysis")
        print(f"{'='*60}")
        
        comparative_results = self.generate_comparative_analysis()
        self.save_batch_results(comparative_results)
        self.generate_batch_dashboard(comparative_results)
        
        return comparative_results
    
    def generate_comparative_analysis(self):
        """Generate comparative analysis across all documents"""
        successful_results = [r for r in self.batch_results if r['success']]
        
        if not successful_results:
            return {"error": "No successful analyses to compare"}
        
        comparative = {
            'batch_summary': {
                'total_files': len(self.batch_results),
                'successful_analyses': len(successful_results),
                'failed_analyses': len(self.batch_results) - len(successful_results),
                'success_rate': len(successful_results) / len(self.batch_results) * 100
            },
            'entity_comparison': self.compare_entities(),
            'category_distribution': self.analyze_category_distribution(),
            'relationship_patterns': self.analyze_relationship_patterns(),
            'temporal_coverage': self.analyze_temporal_coverage(),
            'geographic_coverage': self.analyze_geographic_coverage(),
            'key_insights': self.generate_comparative_insights(),
            'processing_timestamp': datetime.now(timezone.utc).isoformat(),
            'individual_results': self.batch_results
        }
        
        return comparative
    
    def compare_entities(self):
        """Compare entities across all documents"""
        entity_stats = {}
        all_entities = set()
        
        for result in self.batch_results:
            if not result['success']:
                continue
                
            filename = result['filename']
            categories = result['results']['categorized_entities']
            
            entity_stats[filename] = {}
            
            for category, entities in categories.items():
                count = len(entities) if entities else 0
                entity_stats[filename][category] = count
                
                if entities:
                    for entity in entities:
                        all_entities.add(entity['name'])
        
        return {
            'entity_counts_by_document': entity_stats,
            'unique_entities_total': len(all_entities),
            'most_common_entities': self.find_common_entities()
        }
    
    def find_common_entities(self):
        """Find entities that appear in multiple documents"""
        entity_frequency = {}
        
        for result in self.batch_results:
            if not result['success']:
                continue
                
            categories = result['results']['categorized_entities']
            document_entities = set()
            
            for category, entities in categories.items():
                if entities:
                    for entity in entities:
                        document_entities.add(entity['name'])
            
            for entity in document_entities:
                entity_frequency[entity] = entity_frequency.get(entity, 0) + 1
        
        # Sort by frequency
        common_entities = sorted(entity_frequency.items(), key=lambda x: x[1], reverse=True)
        return common_entities[:10]  # Top 10 most common
    
    def analyze_category_distribution(self):
        """Analyze how entities are distributed across categories"""
        category_totals = {}
        
        for result in self.batch_results:
            if not result['success']:
                continue
                
            categories = result['results']['categorized_entities']
            
            for category, entities in categories.items():
                count = len(entities) if entities else 0
                category_totals[category] = category_totals.get(category, 0) + count
        
        return category_totals
    
    def analyze_relationship_patterns(self):
        """Analyze relationship patterns across documents"""
        relationship_stats = {}
        
        for result in self.batch_results:
            if not result['success']:
                continue
                
            filename = result['filename']
            relationships = result['results']['relationship_analysis']
            
            relationship_stats[filename] = {}
            for rel_type, rels in relationships.items():
                relationship_stats[filename][rel_type] = len(rels) if rels else 0
        
        return relationship_stats
    
    def analyze_temporal_coverage(self):
        """Analyze temporal aspects across documents"""
        temporal_data = []
        
        for result in self.batch_results:
            if not result['success']:
                continue
                
            filename = result['filename']
            pub_year = None
            
            # Try to get publication year from metadata
            if 'raw_extraction' in result['results']:
                metadata = result['results']['raw_extraction'].get('metadata', {})
                pub_year = metadata.get('publication_year')
            
            temporal_data.append({
                'filename': filename,
                'publication_year': pub_year
            })
        
        return temporal_data
    
    def analyze_geographic_coverage(self):
        """Analyze geographic coverage across documents"""
        geographic_data = {}
        
        for result in self.batch_results:
            if not result['success']:
                continue
                
            filename = result['filename']
            locations = []
            
            categories = result['results']['categorized_entities']
            if 'geographic_locations' in categories:
                locations = [entity['name'] for entity in categories['geographic_locations']]
            
            geographic_data[filename] = locations
        
        return geographic_data
    
    def generate_comparative_insights(self):
        """Generate insights from comparative analysis"""
        insights = []
        successful_count = len([r for r in self.batch_results if r['success']])
        
        if successful_count >= 2:
            insights.append(f"Successfully analyzed {successful_count} documents for comparative study")
            
            # Find documents with most entities
            entity_counts = {}
            for result in self.batch_results:
                if result['success']:
                    total_entities = result['results']['insights']['summary']['total_entities']
                    entity_counts[result['filename']] = total_entities
            
            if entity_counts:
                max_entities_doc = max(entity_counts, key=entity_counts.get)
                insights.append(f"Document with richest content: {max_entities_doc} ({entity_counts[max_entities_doc]} entities)")
            
            # Analyze common themes
            common_entities = self.find_common_entities()
            if common_entities:
                top_entity = common_entities[0]
                insights.append(f"Most frequently mentioned entity: '{top_entity[0]}' (appears in {top_entity[1]} documents)")
        
        return insights
    
    def save_batch_results(self, comparative_results):
        """Save batch analysis results"""
        batch_file = self.output_dir / f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(comparative_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Batch analysis saved to: {batch_file}")
        return batch_file
    
    def generate_batch_dashboard(self, comparative_results):
        """Generate comparative dashboard"""
        template_path = Path(__file__).parents[1] / "batch_dashboard_template.html"
        
        # Create batch dashboard template if it doesn't exist
        if not template_path.exists():
            self.create_batch_dashboard_template(template_path)
        
        dashboard_path = self.output_dir / f"batch_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Inject data
        data_script = f"""
        <script>
        const BATCH_DATA = {json.dumps(comparative_results, indent=2, ensure_ascii=False)};
        
        function loadBatchData() {{
            displayBatchStats(BATCH_DATA.batch_summary);
            displayEntityComparison(BATCH_DATA.entity_comparison);
            displayCategoryDistribution(BATCH_DATA.category_distribution);
            displayGeographicCoverage(BATCH_DATA.geographic_coverage);
            displayInsights(BATCH_DATA.key_insights);
        }}
        </script>
        """
        
        enhanced_template = template.replace('</body>', f'{data_script}\n</body>')
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_template)
        
        print(f"📊 Batch dashboard: {dashboard_path}")
        webbrowser.open(f'file://{dashboard_path.absolute()}')
        print(f"🌐 Batch dashboard opened in browser")
    
    def create_batch_dashboard_template(self, template_path):
        """Create batch dashboard template"""
        batch_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch Geodata Analysis Dashboard</title>
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --light-bg: #ecf0f1;
            --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--primary-color);
            background-color: var(--light-bg);
        }

        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
        }

        .header h1 {
            color: var(--primary-color);
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
            text-align: center;
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .section {
            background: white;
            margin-bottom: 30px;
            padding: 25px;
            border-radius: 10px;
            box-shadow: var(--card-shadow);
        }

        .section-title {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: var(--primary-color);
            border-bottom: 3px solid var(--secondary-color);
            padding-bottom: 10px;
        }

        .document-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .document-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--secondary-color);
        }

        .entity-chart, .category-chart {
            margin-top: 20px;
        }

        .bar {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }

        .bar-label {
            width: 150px;
            font-size: 0.9em;
        }

        .bar-fill {
            height: 20px;
            background: var(--secondary-color);
            margin-right: 10px;
            border-radius: 3px;
        }

        .insight-item {
            background: #e8f4f8;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid var(--success-color);
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>📊 Batch Geodata Analysis Dashboard</h1>
            <div class="subtitle">Comparative Analysis Across Multiple Documents</div>
        </div>

        <div class="stats-grid" id="statsGrid">
            <!-- Stats will be populated by JavaScript -->
        </div>

        <div class="section">
            <h2 class="section-title">📈 Entity Comparison</h2>
            <div id="entityComparison">
                <!-- Entity comparison will be populated -->
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">🏷️ Category Distribution</h2>
            <div id="categoryDistribution">
                <!-- Category distribution will be populated -->
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">🗺️ Geographic Coverage</h2>
            <div id="geographicCoverage">
                <!-- Geographic coverage will be populated -->
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">💡 Key Insights</h2>
            <div id="insights">
                <!-- Insights will be populated -->
            </div>
        </div>
    </div>

    <script>
        function displayBatchStats(summary) {
            const statsGrid = document.getElementById('statsGrid');
            const stats = [
                { label: 'Total Files', value: summary.total_files, color: 'var(--primary-color)' },
                { label: 'Successful', value: summary.successful_analyses, color: 'var(--success-color)' },
                { label: 'Failed', value: summary.failed_analyses, color: 'var(--danger-color)' },
                { label: 'Success Rate', value: summary.success_rate.toFixed(1) + '%', color: 'var(--secondary-color)' }
            ];

            statsGrid.innerHTML = stats.map(stat => `
                <div class="stat-card">
                    <div class="stat-number" style="color: ${stat.color}">${stat.value}</div>
                    <div class="stat-label">${stat.label}</div>
                </div>
            `).join('');
        }

        function displayEntityComparison(entityData) {
            const container = document.getElementById('entityComparison');
            const entityCounts = entityData.entity_counts_by_document;
            
            let html = '<div class="document-grid">';
            for (const [filename, counts] of Object.entries(entityCounts)) {
                const totalEntities = Object.values(counts).reduce((sum, count) => sum + count, 0);
                html += `
                    <div class="document-card">
                        <h4>${filename}</h4>
                        <p><strong>Total Entities:</strong> ${totalEntities}</p>
                        ${Object.entries(counts).filter(([_, count]) => count > 0).map(([category, count]) => 
                            `<div>${category.replace(/_/g, ' ')}: ${count}</div>`
                        ).join('')}
                    </div>
                `;
            }
            html += '</div>';
            
            if (entityData.most_common_entities && entityData.most_common_entities.length > 0) {
                html += '<h3>Most Common Entities Across Documents:</h3>';
                html += entityData.most_common_entities.map(([entity, count]) => 
                    `<div class="insight-item">${entity} (appears in ${count} documents)</div>`
                ).join('');
            }
            
            container.innerHTML = html;
        }

        function displayCategoryDistribution(categoryData) {
            const container = document.getElementById('categoryDistribution');
            const maxCount = Math.max(...Object.values(categoryData));
            
            let html = '<div class="category-chart">';
            for (const [category, count] of Object.entries(categoryData)) {
                if (count > 0) {
                    const percentage = (count / maxCount) * 100;
                    html += `
                        <div class="bar">
                            <div class="bar-label">${category.replace(/_/g, ' ')}</div>
                            <div class="bar-fill" style="width: ${percentage}%;"></div>
                            <span>${count}</span>
                        </div>
                    `;
                }
            }
            html += '</div>';
            
            container.innerHTML = html;
        }

        function displayGeographicCoverage(geoData) {
            const container = document.getElementById('geographicCoverage');
            
            let html = '<div class="document-grid">';
            for (const [filename, locations] of Object.entries(geoData)) {
                html += `
                    <div class="document-card">
                        <h4>${filename}</h4>
                        <p><strong>Locations:</strong> ${locations.length}</p>
                        ${locations.map(loc => `<span class="entity-tag">${loc}</span>`).join(' ')}
                    </div>
                `;
            }
            html += '</div>';
            
            container.innerHTML = html;
        }

        function displayInsights(insights) {
            const container = document.getElementById('insights');
            
            container.innerHTML = insights.map(insight => 
                `<div class="insight-item">${insight}</div>`
            ).join('');
        }

        // Load data when page loads
        window.addEventListener('DOMContentLoaded', loadBatchData);
    </script>
</body>
</html>'''
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(batch_template)

def main():
    """Main function for batch processing"""
    print("🚀 Starting Batch Geodata Analysis...")
    
    config = load_config()
    batch_analyzer = BatchGeodataAnalyzer(config)
    
    # Process PDFs in the raw data directory
    raw_dir = Path(config["data_paths"]["raw_dir"]) / "theses-WAXI"
    
    # Process a limited number of files for demonstration
    results = batch_analyzer.process_batch(raw_dir, max_files=3)
    
    print("\n" + "="*60)
    print("📊 BATCH ANALYSIS SUMMARY")
    print("="*60)
    
    if 'batch_summary' in results:
        summary = results['batch_summary']
        print(f"📁 Total files processed: {summary['total_files']}")
        print(f"✅ Successful analyses: {summary['successful_analyses']}")
        print(f"❌ Failed analyses: {summary['failed_analyses']}")
        print(f"📈 Success rate: {summary['success_rate']:.1f}%")
        
        if 'key_insights' in results:
            print(f"\n💡 Key Insights:")
            for insight in results['key_insights']:
                print(f"  • {insight}")
    
    print("\n✨ Batch analysis completed!")

if __name__ == "__main__":
    main()

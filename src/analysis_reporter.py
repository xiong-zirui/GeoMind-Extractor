import json
from pathlib import Path
from datetime import datetime
import webbrowser

def generate_analysis_report(processed_dir):
    """Generate a comprehensive analysis report"""
    
    # Find the latest analysis files
    analysis_files = list(Path(processed_dir).glob("*_complete_analysis.json"))
    if not analysis_files:
        print("❌ No analysis files found")
        return
    
    latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
    print(f"📋 Reading analysis from: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract information
    doc_info = data['document_info']
    categories = data['categorized_entities']
    relationships = data['relationship_analysis']
    insights = data['insights']
    raw_data = data['raw_extraction']
    
    print("\n" + "="*80)
    print("📊 GEODATA EXTRACTION & ANALYSIS REPORT")
    print("="*80)
    
    # Document Information
    print(f"\n📄 Document: {doc_info['filename']}")
    print(f"⏰ Processed: {doc_info['processing_time']}")
    print(f"🎯 Confidence Scores:")
    print(f"   • Metadata: {doc_info['confidence_scores']['metadata']*100:.1f}%")
    print(f"   • Knowledge Graph: {doc_info['confidence_scores']['knowledge_graph']*100:.1f}%")
    
    # Metadata Summary
    metadata = raw_data['metadata']
    print(f"\n📑 Document Metadata:")
    print(f"   • Title: {metadata['title']}")
    print(f"   • Author(s): {', '.join(metadata['authors'])}")
    print(f"   • Year: {metadata['publication_year']}")
    print(f"   • Keywords: {', '.join(metadata['keywords'])}")
    
    # Categories Analysis
    print(f"\n🏷️ ENTITY CATEGORIZATION:")
    total_entities = sum(len(entities) for entities in categories.values() if entities)
    print(f"   📊 Total Categorized Entities: {total_entities}")
    
    for category, entities in categories.items():
        if entities:
            category_name = category.replace('_', ' ').title()
            print(f"\n   📁 {category_name} ({len(entities)} entities):")
            for entity in entities:
                print(f"      • {entity['name']} ({entity['type']})")
    
    # Relationships Analysis
    print(f"\n🔗 RELATIONSHIP ANALYSIS:")
    total_relationships = sum(len(rels) for rels in relationships.values() if rels)
    print(f"   📊 Total Relationships: {total_relationships}")
    
    for rel_type, rels in relationships.items():
        if rels:
            type_name = rel_type.replace('_', ' ').title()
            print(f"\n   🔗 {type_name} ({len(rels)} relationships):")
            for rel in rels[:5]:  # Show first 5
                print(f"      • {rel['source']} → {rel['relationship']} → {rel['target']}")
            if len(rels) > 5:
                print(f"      ... and {len(rels) - 5} more")
    
    # Key Insights
    print(f"\n💡 KEY INSIGHTS:")
    for finding in insights['key_findings']:
        print(f"   • {finding}")
    
    if insights['geological_context']:
        print(f"\n🗺️ GEOLOGICAL CONTEXT:")
        for key, value in insights['geological_context'].items():
            context_name = key.replace('_', ' ').title()
            if isinstance(value, list):
                print(f"   • {context_name}: {', '.join(value)}")
            else:
                print(f"   • {context_name}: {value}")
    
    print(f"\n📋 RECOMMENDATIONS:")
    for rec in insights['recommendations']:
        print(f"   • {rec}")
    
    # Processing Statistics
    print(f"\n📈 PROCESSING STATISTICS:")
    summary = insights['summary']
    print(f"   • Total Entities Extracted: {summary['total_entities']}")
    print(f"   • Total Relationships: {summary['total_relationships']}")
    print(f"   • Categories with Data: {len([k for k, v in summary['categories_found'].items() if v > 0])}")
    print(f"   • Category Distribution:")
    for category, count in summary['categories_found'].items():
        category_name = category.replace('_', ' ').title()
        print(f"     - {category_name}: {count}")
    
    # Data Quality Assessment
    print(f"\n🎯 DATA QUALITY ASSESSMENT:")
    
    # Check extraction completeness
    has_metadata = bool(metadata['title'] and metadata['authors'])
    has_entities = summary['total_entities'] > 0
    has_relationships = summary['total_relationships'] > 0
    has_categories = len(summary['categories_found']) > 0
    
    quality_score = sum([has_metadata, has_entities, has_relationships, has_categories]) / 4 * 100
    
    print(f"   • Overall Quality Score: {quality_score:.1f}%")
    print(f"   • Metadata Extraction: {'✅ Success' if has_metadata else '❌ Failed'}")
    print(f"   • Entity Extraction: {'✅ Success' if has_entities else '❌ Failed'}")
    print(f"   • Relationship Extraction: {'✅ Success' if has_relationships else '❌ Failed'}")
    print(f"   • Categorization: {'✅ Success' if has_categories else '❌ Failed'}")
    
    # Identify areas for improvement
    print(f"\n🔧 AREAS FOR IMPROVEMENT:")
    
    if not raw_data['extracted_tables']:
        print(f"   • Table extraction failed - needs improvement in structured data parsing")
    
    empty_categories = [k.replace('_', ' ').title() for k, v in categories.items() if not v]
    if empty_categories:
        print(f"   • Missing categories: {', '.join(empty_categories[:3])}")
        if len(empty_categories) > 3:
            print(f"     and {len(empty_categories) - 3} more...")
    
    if summary['total_relationships'] < summary['total_entities']:
        print(f"   • Low relationship density - could extract more entity connections")
    
    print(f"\n" + "="*80)
    print("✨ ANALYSIS COMPLETE")
    print("="*80)
    
    # Generate a simple text report
    report_file = Path(processed_dir) / f"{latest_file.stem}_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("GEODATA EXTRACTION & ANALYSIS REPORT\n")
        f.write("="*50 + "\n\n")
        f.write(f"Document: {doc_info['filename']}\n")
        f.write(f"Processed: {doc_info['processing_time']}\n\n")
        
        f.write("SUMMARY:\n")
        f.write(f"- Total Entities: {summary['total_entities']}\n")
        f.write(f"- Total Relationships: {summary['total_relationships']}\n")
        f.write(f"- Quality Score: {quality_score:.1f}%\n\n")
        
        f.write("CATEGORIES:\n")
        for category, entities in categories.items():
            if entities:
                f.write(f"- {category.replace('_', ' ').title()}: {len(entities)} entities\n")
        
        f.write("\nKEY FINDINGS:\n")
        for finding in insights['key_findings']:
            f.write(f"- {finding}\n")
    
    print(f"📄 Text report saved to: {report_file}")

if __name__ == "__main__":
    processed_dir = "data/processed"
    generate_analysis_report(processed_dir)

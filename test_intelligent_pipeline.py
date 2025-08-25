#!/usr/bin/env python3
"""
Test script for the Intelligent Knowledge Synthesis Pipeline
This script demonstrates the three-phase knowledge synthesis approach in mock mode.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import webbrowser
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the intelligent pipeline
from debug import IntelligentKnowledgePipeline, create_intelligent_html_report

def main():
    """
    Test the Intelligent Knowledge Synthesis Pipeline in mock mode.
    """
    
    print("🚀 Testing Intelligent Knowledge Synthesis Pipeline")
    print("🧪 Running in MOCK mode (no API calls required)")
    print("="*60)
    
    # Initialize pipeline in mock mode
    pipeline = IntelligentKnowledgePipeline(mock_mode=True)
    
    # Test with sample PDF
    test_pdf = "data/raw/theses-WAXI/2015_Fougerouse_Geometry and genesis of the giant Obuasi gold deposit, Ghana revised.pdf"
    
    if not Path(test_pdf).exists():
        print(f"❌ Test PDF not found: {test_pdf}")
        print("Available PDFs:")
        for pdf_file in Path("data/raw/theses-WAXI/").glob("*.pdf"):
            print(f"  - {pdf_file}")
        return
    
    print(f"📁 Processing: {Path(test_pdf).name}")
    
    try:
        # Run the complete intelligent pipeline
        results = pipeline.process_document(test_pdf)
        
        if "error" in results:
            print(f"❌ Pipeline failed: {results['error']}")
            return
        
        # Generate enhanced HTML report
        pdf_name = Path(test_pdf).stem
        html_content = create_intelligent_html_report(results, pdf_name)
        
        # Save the report
        report_path = f"intelligent_synthesis_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ Demo report generated: {report_path}")
        
        # Save detailed JSON results
        json_path = f"intelligent_synthesis_demo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Detailed demo data saved: {json_path}")
        
        # Open the report in browser
        full_path = Path(report_path).absolute()
        webbrowser.open(f'file://{full_path}')
        print(f"🌐 Opening demo report in browser...")
        
        # Print summary of the intelligent analysis
        synthesis = results.get("phase_3_synthesis", {})
        summary = synthesis.get("synthesis_summary", {})
        
        print(f"\n📊 INTELLIGENT KNOWLEDGE SYNTHESIS SUMMARY:")
        print(f"  📋 Document Value Assessment: {summary.get('document_value_assessment', 'Unknown')}")
        print(f"  📊 Data Completeness: {summary.get('data_completeness', 'Unknown')}")
        print(f"  🗺️  Spatial Coverage: {summary.get('spatial_coverage', 'Unknown')}")
        print(f"  🔍 Key Knowledge Contributions: {len(summary.get('key_contributions', []))}")
        
        quality = synthesis.get("quality_metrics", {})
        print(f"  ✅ Cross-validation Score: {quality.get('cross_validation_score', 'N/A')}")
        print(f"  🔬 Data Reliability: {quality.get('data_reliability', 'N/A')}")
        print(f"  📈 Completeness: {quality.get('completeness_percentage', 'N/A')}%")
        
        # Show key contributions
        contributions = summary.get('key_contributions', [])
        if contributions:
            print(f"\n🎯 KEY KNOWLEDGE CONTRIBUTIONS:")
            for i, contribution in enumerate(contributions, 1):
                print(f"     {i}. {contribution}")
        
        # Show database-ready records count
        db_records = synthesis.get("database_ready_records", {})
        print(f"\n💾 DATABASE-READY RECORDS:")
        print(f"  📍 Location Records: {len(db_records.get('location_records', []))}")
        print(f"  ⚗️  Geochemistry Records: {len(db_records.get('geochemistry_records', []))}")
        print(f"  🗿 Geological Units Records: {len(db_records.get('geological_units_records', []))}")
        
        print(f"\n🎉 Intelligent Knowledge Synthesis Pipeline Demo Complete!")
        print(f"   This demonstrates how the three-phase approach transforms")
        print(f"   unstructured geological documents into structured, database-ready knowledge.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

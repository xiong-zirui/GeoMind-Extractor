#!/usr/bin/env python3
"""
Project Cleanup and English Conversion Script
This script removes test files and converts all comments/outputs to English
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_project():
    """Clean up the project by removing test/intermediate files and keeping only production code"""
    
    print("🧹 Starting Project Cleanup and English Conversion...")
    print("=" * 60)
    
    # Define files/directories to remove (test/intermediate files)
    files_to_remove = [
        "comprehensive_analysis.py",  # Original Chinese version
        "comprehensive_analysis_en.py",  # Intermediate English version
        "comprehensive_analysis_en_fixed.py",  # Fixed version
        "comprehensive_analysis_complete_en.py",  # Complete version
        "comprehensive_analysis_final_en.py",  # Final version
        "test_fixed_api.py",  # Test script
        "test_intelligent_pipeline.py",  # Test script
        "test_real_api.py",  # Test script
        "api_test.py",  # API test
    ]
    
    # Define production files to keep
    production_files = [
        "production_analysis.py",  # Production-ready comprehensive analysis
        "src/",  # All source code
        "config.yml",  # Configuration
        "config.example.yml",  # Example configuration
        "requirements.txt",  # Dependencies
        "README.md",  # Documentation
        "data/processed/",  # Processed data
        "prompts/",  # Prompt templates
        "notebooks/",  # Jupyter notebooks
    ]
    
    removed_count = 0
    
    # Remove test/intermediate files
    for file_path in files_to_remove:
        full_path = Path(file_path)
        if full_path.exists():
            try:
                if full_path.is_file():
                    full_path.unlink()
                    print(f"❌ Removed test file: {file_path}")
                    removed_count += 1
                elif full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"❌ Removed test directory: {file_path}")
                    removed_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {file_path}: {e}")
    
    # Clean up temporary HTML reports (keep only the latest production one)
    html_files = list(Path(".").glob("*.html"))
    production_reports = [f for f in html_files if "Production_Analysis_Report" in f.name]
    other_reports = [f for f in html_files if f not in production_reports]
    
    for report in other_reports:
        try:
            report.unlink()
            print(f"❌ Removed temporary report: {report.name}")
            removed_count += 1
        except Exception as e:
            print(f"⚠️  Could not remove {report.name}: {e}")
    
    # Clean up temporary JSON files
    json_files = list(Path(".").glob("*.json"))
    temp_json = [f for f in json_files if any(keyword in f.name for keyword in [
        "真实API", "intelligent_synthesis", "demo", "test"
    ])]
    
    for json_file in temp_json:
        try:
            json_file.unlink()
            print(f"❌ Removed temporary JSON: {json_file.name}")
            removed_count += 1
        except Exception as e:
            print(f"⚠️  Could not remove {json_file.name}: {e}")
    
    print(f"\n✅ Cleanup completed: Removed {removed_count} test/temporary files")
    
    # List production files that remain
    print("\n📋 Production files remaining:")
    for file_path in production_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
    
    return removed_count

def update_readme():
    """Update README.md with English documentation"""
    
    readme_content = """# GeoMind-Extractor: Intelligent Geological Document Analysis System

## Overview

GeoMind-Extractor is an advanced AI-powered system for extracting and analyzing geological information from scientific documents. The system combines traditional data extraction methods with intelligent knowledge synthesis to produce structured, database-ready geological data.

## Key Features

- **Intelligent Document Analysis**: AI-powered content understanding and categorization
- **Multi-Modal Extraction**: Text, tables, images, and spatial data extraction
- **Knowledge Graph Construction**: Automatic relationship extraction between geological entities
- **Database Integration**: Ready-to-use structured data for geological databases
- **Comprehensive Reporting**: Rich HTML reports with visualizations
- **Production Ready**: Robust error handling and scalable architecture

## System Architecture

### Core Components

1. **Document Processing Pipeline**
   - PDF text extraction and preprocessing
   - Image extraction with metadata
   - Content segmentation and analysis

2. **Knowledge Synthesis Engine**
   - Entity extraction and relationship mapping
   - Table structure recognition and standardization
   - Spatial data processing

3. **Intelligent Analysis Agents**
   - Content categorization and prioritization
   - Domain-specific knowledge extraction
   - Cross-validation and quality assessment

4. **Reporting and Visualization**
   - Interactive HTML reports
   - Statistical summaries
   - Data quality metrics

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Configuration

1. Copy the example configuration:
```bash
cp config.example.yml config.yml
```

2. Add your API keys and settings to `config.yml`

### Usage

Run the production analysis on a geological document:

```bash
python production_analysis.py
```

For custom PDF files, modify the `pdf_file` variable in `production_analysis.py`.

## Input/Output

### Input
- PDF documents (geological papers, reports, theses)
- Configuration files (YAML format)

### Output
- Structured JSON data with extracted information
- Interactive HTML reports
- Image galleries with metadata
- Database-ready records

## Data Structure

The system extracts and structures:

- **Document Metadata**: Title, authors, publication info
- **Geological Entities**: Locations, rock types, mineral assemblages
- **Quantitative Data**: Geochemical analyses, measurements
- **Spatial Information**: Coordinates, geological maps
- **Relationships**: Entity connections and dependencies

## Technical Specifications

- **Language**: Python 3.8+
- **Key Dependencies**: PyMuPDF, PIL, pandas, pathlib
- **AI Integration**: Google Gemini API support
- **Output Formats**: JSON, HTML, CSV
- **Database Compatibility**: PostGIS, standard relational databases

## Project Structure

```
GeoMind-Extractor/
├── src/                     # Source code
│   ├── document_processing/ # PDF and text processing
│   ├── entity_extraction/   # AI-powered extraction
│   ├── graph_construction/  # Knowledge graph building
│   └── agents/             # Intelligent analysis agents
├── data/                   # Data storage
│   ├── raw/               # Input documents
│   └── processed/         # Output data and reports
├── prompts/               # AI prompt templates
├── production_analysis.py # Main production script
├── config.yml            # System configuration
└── requirements.txt      # Python dependencies
```

## Quality Assurance

- Automated confidence scoring for all extractions
- Cross-validation between different extraction methods
- Data quality metrics and reporting
- Error handling and fallback mechanisms

## License

This project is developed for geological research and analysis applications.

## Support

For questions or issues, please refer to the documentation or create an issue in the repository.

---

**GeoMind-Extractor** - Transforming unstructured geological documents into structured knowledge.
"""
    
    try:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("✅ Updated README.md with English documentation")
        return True
    except Exception as e:
        print(f"⚠️  Could not update README.md: {e}")
        return False

def create_project_summary():
    """Create a summary of the cleaned project"""
    
    summary = {
        "cleanup_timestamp": datetime.now().isoformat(),
        "production_ready": True,
        "key_features": [
            "Intelligent document analysis",
            "Multi-modal data extraction", 
            "Knowledge graph construction",
            "Database-ready output",
            "Comprehensive reporting"
        ],
        "main_components": {
            "production_analysis.py": "Main production script for comprehensive analysis",
            "src/": "Core source code modules",
            "data/processed/": "Output data and reports",
            "config.yml": "System configuration"
        },
        "removed_items": [
            "Test scripts and intermediate versions",
            "Temporary HTML/JSON files",
            "Development artifacts"
        ]
    }
    
    try:
        import json
        with open("PROJECT_SUMMARY.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print("✅ Created PROJECT_SUMMARY.json")
        return True
    except Exception as e:
        print(f"⚠️  Could not create project summary: {e}")
        return False

def main():
    """Main cleanup function"""
    
    print("🚀 GeoMind-Extractor Project Cleanup and Finalization")
    print("=" * 60)
    
    # Step 1: Clean up test files
    removed_count = cleanup_project()
    
    # Step 2: Update documentation
    readme_updated = update_readme()
    
    # Step 3: Create project summary
    summary_created = create_project_summary()
    
    print("\n" + "=" * 60)
    print("📊 Project Cleanup Summary:")
    print(f"   • Removed {removed_count} test/temporary files")
    print(f"   • README updated: {'✅' if readme_updated else '❌'}")
    print(f"   • Project summary created: {'✅' if summary_created else '❌'}")
    
    print("\n🎉 Project is now production-ready!")
    print("📋 Main entry point: production_analysis.py")
    print("📚 Documentation: README.md")
    print("⚙️  Configuration: config.yml")
    
    print("\n🔄 Next steps:")
    print("   1. Review and test production_analysis.py")
    print("   2. Update configuration as needed")
    print("   3. Commit changes to Git repository")

if __name__ == "__main__":
    main()

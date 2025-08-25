# Usage Guide - GeoMind-Extractor

## Quick Start

### 1. Run the Main Analysis
```bash
python comprehensive_analysis_final_en.py
```

### 2. Expected Results
- HTML report generated in `data/processed/`
- Images extracted to `data/processed/images/`
- Console output in English

### 3. View Results
The HTML report will automatically open in your browser.

## Working Scripts

### Primary (Recommended)
- `comprehensive_analysis_final_en.py` - Final working version

### Alternatives  
- `production_analysis.py` - Clean production code
- `comprehensive_analysis_complete_en.py` - Full feature set

## Customization

### Change Input Document
Edit the PDF filename in the script:
```python
pdf_file = "your_document.pdf"  # Change this line
```

### Output Location
Reports are saved to `data/processed/` automatically.

## Troubleshooting

### Common Issues
1. **Missing images**: Check `data/processed/images/` directory
2. **Report not opening**: Check browser settings
3. **File errors**: Ensure input PDF exists

### Success Indicators
- Console shows "✅ Found X images"
- HTML report path displayed
- Browser opens automatically

## Features Working
- ✅ PDF processing
- ✅ Image extraction  
- ✅ Table processing
- ✅ HTML generation
- ✅ English interface

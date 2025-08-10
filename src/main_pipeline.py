# src/main_pipeline.py

import pathlib
import json
import sys

# Add the project root to the Python path to resolve imports
project_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src import pdf_processor
from src.agent_interaction import configure_agent

def run_pipeline():
    """
    Finds all PDFs in the raw data directory and processes them one by one.
    """
    # Define project directories
    base_dir = pathlib.Path(__file__).resolve().parents[1]
    raw_data_dir = base_dir / 'data' / 'raw'
    processed_data_dir = base_dir / 'data' / 'processed'
    
    # Create processed directory if it doesn't exist
    processed_data_dir.mkdir(exist_ok=True)
    
    # Configure the agent once for the entire pipeline
    print("INFO: Initializing the agent for the pipeline...")
    try:
        agent = configure_agent()
    except ValueError as e:
        print(e)
        return # Exit if API key is not configured

    # Find and process only the first PDF to save costs
    pdf_files = sorted(list(raw_data_dir.glob('*.pdf'))) # Sort to ensure consistent order
    if not pdf_files:
        print(f"WARNING: No PDF files found in '{raw_data_dir}'. Please add your PDFs and run again.")
        return
        
    print(f"INFO: Found {len(pdf_files)} PDF(s). Processing only the first one for this run.")
    
    # --- Process only the first PDF ---
    first_pdf_path = pdf_files[0]
    
    result = pdf_processor.process_single_pdf(first_pdf_path, agent)
    
    # Save the result to a JSON file
    output_filename = first_pdf_path.stem + '_extraction_result.json'
    output_path = processed_data_dir / output_filename
    
    # A simple custom encoder to handle Pydantic models
    class PydanticEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, 'dict'):
                return obj.dict()
            return json.JSONEncoder.default(self, obj)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, cls=PydanticEncoder)
        
    print(f"SUCCESS: Pipeline complete for '{first_pdf_path.name}'. Results saved to '{output_path}'.\n")

if __name__ == "__main__":
    run_pipeline()
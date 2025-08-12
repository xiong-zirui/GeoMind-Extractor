# src/main.py

import pathlib
import json
import sys
import argparse
import logging

# Add the 'src' directory to the Python path
project_root = pathlib.Path(__file__).resolve().parent
sys.path.append(str(project_root))

from document_processing import pdf_processor
from entity_extraction.llm_extractor import configure_agent
from graph_construction.neo4j_loader import Neo4jLoader
from models import KnowledgeGraph

from config import config

def run_pipeline(input_file=None, input_dir=None, output_dir=None, load_to_neo4j=False):
    """
    Finds all PDFs in the raw data directory, processes them, and optionally loads to Neo4j.
    """
    # --- Setup ---
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    base_dir = pathlib.Path(__file__).resolve().parents[1]
    
    if output_dir:
        processed_data_dir = pathlib.Path(output_dir)
    else:
        processed_data_dir = base_dir / config['data_paths']['processed_dir']
    
    processed_data_dir.mkdir(exist_ok=True)
    
    logging.info("Initializing the agent for the pipeline...")
    try:
        agent = configure_agent(api_key=config['openai_api_key'])
    except ValueError as e:
        logging.error(e)
        return

    # --- PDF File Discovery ---
    if input_file:
        pdf_files = [pathlib.Path(input_file)]
    else:
        raw_data_dir = pathlib.Path(input_dir) if input_dir else base_dir / config['data_paths']['raw_theses_dir']
        pdf_files = sorted(list(raw_data_dir.glob('**/*.pdf')))

    if not pdf_files:
        logging.warning("No PDF files found. Please check the input path.")
        return
        
    logging.info(f"Found {len(pdf_files)} PDF(s) to process.")
    
    # --- Neo4j Loader Initialization ---
    neo4j_loader = None
    if load_to_neo4j:
        try:
            neo4j_config = config['neo4j']
            neo4j_loader = Neo4jLoader(
                uri=neo4j_config['uri'],
                user=neo4j_config['user'],
                password=neo4j_config['password'],
                database=neo4j_config.get('database', 'neo4j')
            )
            logging.info("Successfully initialized Neo4j loader.")
        except Exception as e:
            logging.error(f"Failed to initialize Neo4j loader: {e}. Aborting.")
            return

    # --- Main Processing Loop ---
    for pdf_path in pdf_files:
        logging.info(f"--- Processing '{pdf_path.name}' ---")
        
        # 1. Process the PDF to extract structured data
        extraction_result = pdf_processor.process_single_pdf(pdf_path, agent)
        
        # 2. Save the raw extraction result to a JSON file
        output_filename = pdf_path.stem + '_extraction_result.json'
        output_path = processed_data_dir / output_filename
        
        class PydanticEncoder(json.JSONEncoder):
            def default(self, obj):
                if hasattr(obj, 'dict'):
                    return obj.dict()
                return json.JSONEncoder.default(self, obj)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extraction_result, f, indent=2, ensure_ascii=False, cls=PydanticEncoder)
        logging.info(f"Extraction results saved to '{output_path}'.")

        # 3. Load the knowledge graph into Neo4j if requested
        if neo4j_loader and extraction_result.get("knowledge_graph"):
            try:
                kg_data = KnowledgeGraph(**extraction_result["knowledge_graph"])
                neo4j_loader.load_graph(kg_data, source_document=pdf_path.name)
                logging.info(f"Successfully loaded knowledge graph for '{pdf_path.name}' into Neo4j.")
            except Exception as e:
                logging.error(f"Failed to load graph for '{pdf_path.name}' into Neo4j: {e}")

    # --- Cleanup ---
    if neo4j_loader:
        neo4j_loader.close()
    
    logging.info("--- Pipeline finished ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Geodata Extraction Pipeline from PDF documents.")
    
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--input-file", help="Path to a single PDF file to process.")
    input_group.add_argument("--input-dir", help="Path to a directory containing PDF files to process.")

    parser.add_argument("--output-dir", help="Directory to save the extraction results.")
    parser.add_argument("--load-to-neo4j", action='store_true', help="Load the extracted knowledge graph into Neo4j.")

    args = parser.parse_args()

    run_pipeline(
        input_file=args.input_file,
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        load_to_neo4j=args.load_to_neo4j
    )
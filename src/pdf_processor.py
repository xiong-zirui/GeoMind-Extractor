# src/pdf_processor.py

import pathlib
import fitz  # PyMuPDF
import logging
from typing import List
from src import agent_interaction
from datetime import datetime

# --- Text Extraction and Chunking ---

def extract_full_text_from_pdf(pdf_path: pathlib.Path) -> str:
    """
    Extracts plain text from the entire PDF document.
    """
    full_text = ""
    logging.info(f"Extracting full text from '{pdf_path.name}'...")
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                full_text += page.get_text() + "\n"
        return full_text
    except Exception as e:
        logging.error(f"Could not extract text from PDF '{pdf_path.name}'. Error: {e}")
        return ""

def chunk_text_by_paragraph(text: str, min_chunk_size: int = 50) -> List[str]:
    """
    Splits text into semantic chunks based on paragraphs (double newlines)
    and filters out very small, likely irrelevant chunks.
    """
    if not text:
        return []
    
    # Split by double newline, which typically separates paragraphs
    chunks = text.split('\n\n')
    
    # Clean up chunks and filter out small or empty ones
    processed_chunks = [
        chunk.strip().replace('\n', ' ') 
        for chunk in chunks 
        if len(chunk.strip()) > min_chunk_size
    ]
    
    logging.info(f"Split text into {len(processed_chunks)} semantic chunks.")
    return processed_chunks

# --- Main Processing Orchestration ---

def process_single_pdf(pdf_path: pathlib.Path, agent) -> dict:
    """
    Orchestrates the entire extraction process for a single PDF file,
    using semantic chunking for metadata extraction.
    """
    logging.info(f"--- Processing file: {pdf_path.name} ---")
    
    # 1. Extract full text and perform semantic chunking
    full_text = extract_full_text_from_pdf(pdf_path)
    text_chunks = chunk_text_by_paragraph(full_text)
    
    # 2. Extract Metadata from the first significant text chunk (usually the abstract)
    metadata = {}
    if text_chunks:
        first_chunk = text_chunks[0]
        logging.info("Using the first semantic chunk for metadata extraction.")
        metadata = agent_interaction.get_metadata_from_text(agent, first_chunk)
    else:
        logging.warning("No significant text chunks found for metadata extraction.")

    # 3. Extract Table from the entire PDF (this remains unchanged)
    table_data = agent_interaction.get_table_from_pdf(agent, pdf_path)
    
    # 4. Extract Knowledge Graph from the first few chunks
    knowledge_graph = {}
    if text_chunks:
        # Combine the first 3 chunks to provide more context for KG extraction
        kg_context = " ".join(text_chunks[:3])
        logging.info("Using the first three semantic chunks for knowledge graph extraction.")
        knowledge_graph = agent_interaction.get_knowledge_graph_from_text(agent, kg_context)
    else:
        logging.warning("No significant text chunks found for knowledge graph extraction.")

    # 5. Image analysis (Placeholder)
    image_analyses = [{"status": "pending", "comment": "Image analysis not yet implemented."}]
    
    # 6. Assemble the final structured data
    structured_output = {
        "source_file": pdf_path.name,
        "processing_timestamp_utc": datetime.utcnow().isoformat(),
        "metadata": metadata.dict() if metadata else None,
        "extracted_tables": [table_data.dict() if table_data else None],
        "knowledge_graph": knowledge_graph.dict() if knowledge_graph else None,
        "image_analysis": image_analyses
    }
    
    logging.info(f"--- Finished processing: {pdf_path.name} ---")
    return structured_output
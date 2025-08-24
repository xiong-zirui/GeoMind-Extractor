# src/pdf_processor.py

import pathlib
import fitz  # PyMuPDF
import logging
from typing import List
from datetime import datetime

from entity_extraction import llm_extractor

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

def extract_images_from_pdf(pdf_path: pathlib.Path, output_dir: pathlib.Path) -> list:
    """
    Extracts images from a PDF and saves them to a directory.
    Returns a list of paths to the extracted images.
    """
    logging.info(f"Extracting images from {pdf_path.name}...")
    image_paths = []
    output_dir.mkdir(exist_ok=True)
    
    try:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"{pdf_path.stem}_page{page_num+1}_img{img_index}.{image_ext}"
                image_path = output_dir / image_filename
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                image_paths.append(image_path)
        logging.info(f"Extracted {len(image_paths)} images from {pdf_path.name}")
        return image_paths
    except Exception as e:
        logging.error(f"Could not extract images from PDF '{pdf_path.name}'. Error: {e}")
        return []


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
    metadata = None
    if text_chunks:
        first_chunk = text_chunks[0]
        logging.info("Using the first semantic chunk for metadata extraction.")
        metadata = llm_extractor.extract_metadata(agent, first_chunk)
    else:
        logging.warning("No significant text chunks found for metadata extraction.")

    # 3. Extract Tables from the entire document by chunks
    all_tables = []
    logging.info("Scanning document for tables...")
    for chunk in text_chunks:
        tables = llm_extractor.extract_tables(agent, chunk)
        if tables:
            all_tables.extend(tables)
    logging.info(f"Found {len(all_tables)} tables in total.")
    
    # 4. Extract Knowledge Graph from the first few chunks
    knowledge_graph = None
    if text_chunks:
        # Combine the first 5 chunks to provide more context for KG extraction
        kg_context = " ".join(text_chunks[:5])
        logging.info("Using the first five semantic chunks for knowledge graph extraction.")
        knowledge_graph = llm_extractor.extract_knowledge_graph(agent, kg_context)
    else:
        logging.warning("No significant text chunks found for knowledge graph extraction.")

    # 5. Image analysis
    image_dir = pdf_path.parent / "images"
    image_paths = extract_images_from_pdf(pdf_path, image_dir)
    image_analyses = []
    if image_paths:
        # For now, we'll just analyze the first image as a demo
        # A full implementation might loop through all images or select important ones
        first_image = image_paths[0]
        # Provide some context from the text around where the image might be
        # (This is a simplification; a real system would need to locate the image in the text)
        image_context = " ".join(text_chunks[:3]) 
        analysis = llm_extractor.analyze_map_image(agent, first_image, image_context)
        if analysis:
            image_analyses.append(analysis)
    
    # 6. Assemble the final structured data
    structured_output = {
        "source_document": pdf_path.name,
        "processing_timestamp": datetime.utcnow().isoformat(),
        "metadata": metadata.dict() if metadata else None,
        "tables": [table.dict() for table in all_tables],
        "knowledge_graph": knowledge_graph.dict() if knowledge_graph else None,
        "image_analyses": [analysis.dict() for analysis in image_analyses]
    }
    
    logging.info(f"--- Finished processing: {pdf_path.name} ---")
    return structured_output
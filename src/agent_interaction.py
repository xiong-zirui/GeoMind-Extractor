# src/agent_interaction.py

import os
import pathlib
import json
import logging
import time
import hashlib
from typing import Type, TypeVar, Optional, List, Union

import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import ValidationError, BaseModel

# Import our Pydantic models
from src.models import ExtractedMetadata, ExtractedTable, MapAnalysis, KnowledgeGraph

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a generic type for our Pydantic models, ensuring it's a Pydantic BaseModel
T = TypeVar('T', bound=BaseModel)

# --- Cache Configuration ---
CACHE_DIR = pathlib.Path(__file__).resolve().parents[1] / '.cache'
CACHE_FILE = CACHE_DIR / 'api_cache.json'
CACHE_DIR.mkdir(exist_ok=True) # Ensure the cache directory exists

# --- Cache Helper Functions ---
def load_cache() -> dict:
    """Loads the API call cache from the file system."""
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_cache(cache_data: dict):
    """Saves the API call cache to the file system."""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2)

def generate_cache_key(prompt: str, input_data: list) -> str:
    """Generates a unique SHA256 hash key for a given prompt and input data."""
    key_seed = prompt
    # Safely serialize input data to a string for hashing
    for item in input_data[1:]: # Skip the prompt itself which is the first element
        if isinstance(item, str):
            key_seed += item
        elif hasattr(item, 'name'): # Caters to uploaded file objects
            key_seed += item.name
        else:
            # A fallback for other data types
            key_seed += str(item)
    
    return hashlib.sha256(key_seed.encode('utf-8')).hexdigest()


# --- Configuration ---
def configure_agent():
    """
    Loads API key from .env and configures the Gemini model.
    Returns a configured model object.
    """
    dotenv_path = pathlib.Path(__file__).resolve().parents[1] / '.env'
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "YOUR_API_KEY_HERE" in api_key:
        raise ValueError("ERROR: GOOGLE_API_KEY not found or not set in .env file.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    return model

def get_prompt_from_file(prompt_filename: str) -> str:
    """Reads a prompt template from the ../prompts/ directory."""
    prompt_path = pathlib.Path(__file__).resolve().parents[1] / 'prompts' / prompt_filename
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

# --- Core Interaction Logic with Self-Correction and Caching ---
def get_structured_data_with_retry(
    agent,
    model_class: Type[T],
    base_prompt: str,
    input_data: list,
    max_retries: int = 3
) -> Optional[T]:
    """
    A robust function to get structured data from the agent, with validation and self-correction.

    Args:
        agent: The configured generative model.
        model_class: The Pydantic model class to validate the output against.
        base_prompt: The initial prompt for the agent, without feedback.
        input_data: A list containing the prompt and any text/files for the agent.
        max_retries: The maximum number of retries for self-correction.

    Returns:
        An instance of the Pydantic model if successful, otherwise None.
    """
    # --- Caching Logic ---
    cache_key = generate_cache_key(base_prompt, input_data)
    cache = load_cache()
    
    if cache_key in cache:
        logging.info(f"Cache hit! Loading result for key: {cache_key[:10]}...")
        try:
            # Validate cached data against the model, in case the model has changed
            cached_data = model_class.parse_obj(cache[cache_key])
            return cached_data
        except ValidationError as e:
            logging.warning(f"Cached data for key {cache_key[:10]} is invalid, re-fetching. Error: {e}")
            # If validation fails, proceed to fetch from API

    current_input = input_data
    
    for attempt in range(max_retries):
        logging.info(f"Calling agent (Attempt {attempt + 1}/{max_retries})...")
        
        try:
            response = agent.generate_content(current_input)
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            
            try:
                json_data = json.loads(cleaned_text)
                validated_data = model_class.parse_obj(json_data)
                logging.info("Successfully extracted and validated structured data.")
                
                # --- Save to Cache on Success ---
                cache[cache_key] = validated_data.dict()
                save_cache(cache)
                logging.info(f"Saved new result to cache with key: {cache_key[:10]}...")
                
                return validated_data
            except (json.JSONDecodeError, ValidationError) as e:
                logging.warning(f"Attempt {attempt + 1} failed: {type(e).__name__}. Details: {e}")
                if attempt < max_retries - 1:
                    feedback = (
                        "Your previous response was not valid. "
                        f"Error: {e}. "
                        "Please review the required JSON structure, correct the error, and provide only the valid JSON object."
                    )
                    # Rebuild the prompt with feedback for the next attempt
                    new_prompt = f"{base_prompt}\n\n--- FEEDBACK ---\n{feedback}"
                    # The first element of the list is always the prompt
                    current_input[0] = new_prompt
                continue

        except Exception as e:
            logging.error(f"An unexpected error occurred during agent call on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2) # Wait a bit before retrying on general errors

    logging.error(f"Failed to get valid structured data after {max_retries} attempts.")
    return None

# --- Specific Extraction Functions ---
def get_metadata_from_text(agent, text_chunk: str) -> Optional[ExtractedMetadata]:
    """
    Sends a text chunk to the agent and asks for structured metadata.
    """
    logging.info("Extracting metadata from text chunk...")
    base_prompt = get_prompt_from_file('extract_metadata.md')
    
    # The prompt now needs to explicitly ask for JSON matching the Pydantic model
    # (This should be updated in the .md file itself for best practice)
    prompt_with_instructions = base_prompt + "\nPlease return the data as a single JSON object matching the specified structure, including a confidence_score."

    return get_structured_data_with_retry(
        agent=agent,
        model_class=ExtractedMetadata,
        base_prompt=base_prompt,
        input_data=[prompt_with_instructions, text_chunk]
    )

def get_table_from_pdf(agent, pdf_path: pathlib.Path) -> Optional[ExtractedTable]:
    """
    Uploads a PDF and asks the agent to extract a table in a structured format.
    """
    logging.info(f"Uploading '{pdf_path.name}' for table extraction...")
    pdf_file = genai.upload_file(path=pdf_path, display_name=pdf_path.name)
    
    try:
        base_prompt = get_prompt_from_file('extract_table.md')
        prompt_with_instructions = base_prompt + "\nPlease return the data as a single JSON object matching the specified structure, including columns, data, and a confidence_score."

        return get_structured_data_with_retry(
            agent=agent,
            model_class=ExtractedTable,
            base_prompt=base_prompt,
            input_data=[prompt_with_instructions, pdf_file]
        )
    finally:
        # Clean up the uploaded file
        logging.info(f"Deleting uploaded file '{pdf_file.name}' from server.")
        genai.delete_file(pdf_file.name)

def get_knowledge_graph_from_text(agent, text_chunk: str) -> Optional[KnowledgeGraph]:
    """
    Sends a text chunk to the agent and asks for a structured knowledge graph.
    """
    logging.info("Extracting knowledge graph from text chunk...")
    base_prompt = get_prompt_from_file('extract_entities.md')

    return get_structured_data_with_retry(
        agent=agent,
        model_class=KnowledgeGraph,
        base_prompt=base_prompt,
        input_data=[base_prompt, text_chunk]
    )

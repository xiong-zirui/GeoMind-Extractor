# GeoMind Extractor

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-orange)](https://pydantic-docs.helpmanual.io/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Supported-blue.svg)](https://neo4j.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GeoMind Extractor** is an AI-powered pipeline that extracts structured metadata, tables, and builds knowledge graphs from geological PDF documents. It leverages advanced Large Language Models (LLMs) with a robust, self-correcting workflow to transform unstructured scientific papers into machine-readable knowledge.

This project is designed for efficiency and reliability, featuring an automated pipeline that handles everything from PDF parsing to loading data into a graph database.

## Setup Instructions

### 1. Configuration Setup

Before running the system, you need to configure your API keys and database credentials:

1. Copy the example configuration file:
   ```bash
   cp config.example.yml config.yml
   ```

2. Edit `config.yml` and replace the placeholder values:
   ```yaml
   # API keys
   google_api_key: "YOUR_ACTUAL_GOOGLE_API_KEY"
   
   # Neo4j credentials
   neo4j:
     uri: "neo4j://localhost:7687"
     user: "neo4j"
     password: "YOUR_ACTUAL_NEO4J_PASSWORD"
     database: "neo4j"
   ```

### 2. Google AI API Setup

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Replace `YOUR_ACTUAL_GOOGLE_API_KEY` in config.yml with your key

### 3. Neo4j Setup (Optional)

If you want to use the graph database features:

1. Install Neo4j Desktop or run via Docker
2. Create a new database
3. Update the credentials in config.yml

## ✨ Core Features

This project showcases a range of advanced capabilities for building sophisticated, production-ready AI agents.

### 🧠 Intelligent Agent Architecture
- **Modular & Swappable Agents**: The `AgentManager` (`src/agents/manager.py`) allows for easy integration of different LLMs (e.g., Gemini, OpenAI, local models via Ollama).
- **Advanced Prompt Engineering**: Utilizes specialized, role-based prompts for different tasks (metadata, table, and knowledge graph extraction), guiding the LLM with clear, step-by-step instructions.

### 🛡️ Robust and Reliable Extraction
- **Pydantic-Powered Validation**: All LLM outputs are strictly validated against Pydantic models (`src/models.py`), ensuring data integrity and structure.
- **Self-Correction Loop**: If an LLM output fails validation, the system automatically sends the error back to the LLM as feedback, asking it to "self-correct" its response. This significantly increases the reliability of data extraction.

### ⚡ Efficient and Automated Pipeline
- **Intelligent Semantic Chunking**: Instead of naive text splitting, the pipeline first chunks documents by paragraph (`src/document_processing/pdf_processor.py`). This preserves semantic context, providing higher-quality input to the LLM.
- **API Caching**: All calls to the LLM are cached in the `.cache/` directory. This drastically reduces costs and speeds up development by avoiding redundant API calls for the same content.

### 🕸️ Knowledge Graph Construction & Loading
- **Entity & Relationship Extraction**: The pipeline identifies key geological entities (`LOCATION`, `MINERAL`, `FORMATION`, etc.) and the relationships between them (`CONTAINS`, `LOCATED_IN`).
- **Automated Neo4j Loading**: The extracted knowledge graph is automatically loaded into a Neo4j database (`src/graph_construction/neo4j_loader.py`), linking entities to their source document.

## ⚙️ How It Works

The pipeline, orchestrated by `src/main.py`, follows these steps for each PDF document:

1.  **PDF Processing**: The text content is extracted from the PDF using `PyMuPDF`.
2.  **Semantic Chunking**: The text is split into meaningful paragraphs (chunks) to preserve context.
3.  **Multi-Task Extraction**: The agent performs several extraction tasks, each benefiting from caching and self-correction:
    -   **Metadata**: The first chunk (usually the abstract) is used to extract metadata.
    -   **Knowledge Graph**: The first few chunks are used to build a knowledge graph of entities and relationships.
    -   **Tables**: The entire document is analyzed to find and extract significant tables.
4.  **Structured Output**: All extracted information is compiled into a single, clean JSON file in the `data/processed` directory.
5.  **Graph Loading (Optional)**: If configured, the final knowledge graph is loaded into Neo4j.

## 📂 Project Structure

```
Geodata-Extraction-Capstone/
├── .cache/                  # Stores API call cache to reduce costs
├── README.md
├── requirements.txt
├── config.yml               # Main configuration for paths and API keys
├── data/
│   ├── processed/           # Processed JSON outputs
│   └── raw/                 # Raw input PDFs
├── notebooks/
│   └── 1_Data_Exploration_and_Extraction.ipynb # For exploring data
├── prompts/                 # Advanced prompt templates for the LLM
│   ├── extract_entities.md
│   ├── extract_metadata.md
│   └── extract_table.md
└── src/                     # Source code
    ├── __init__.py
    ├── main.py              # Main executable pipeline
    ├── config.py            # Loads configuration
    ├── models.py            # Pydantic models for data validation
    ├── utils.py             # Utility functions
    ├── agents/              # Handles LLM models and management
    │   ├── base.py
    │   ├── gemini.py
    │   └── manager.py
    ├── document_processing/ # Handles PDF parsing and chunking
    │   └── pdf_processor.py
    ├── entity_extraction/   # Handles LLM calls, caching, and self-correction
    │   └── llm_extractor.py
    └── graph_construction/  # Handles Neo4j connection and loading
        └── neo4j_loader.py
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- An API key for your language model provider (e.g., Google, OpenAI).
- Access to a Neo4j instance (optional, for graph loading).

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd Geodata-Extraction-Capstone
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure the project:**
    - Open `config.yml` and fill in your details:
        - `openai_api_key`: Your API key.
        - `neo4j`: Your Neo4j connection details (if used).
        - Update data paths if needed.

### Running the Pipeline
You can run the entire pipeline from the command line.

-   **To process all PDFs in the default directory:**
    ```bash
    python src/main.py
    ```
-   **To process a single PDF file:**
    ```bash
    python src/main.py --input_file /path/to/your/document.pdf
    ```
-   **To process a different directory:**
    ```bash
    python src/main.py --input_dir /path/to/your/pdfs/
    ```
-   **To load the results into Neo4j:**
    Add the `--load` flag to any of the above commands.
    ```bash
    python src/main.py --load
    ```

## 💡 Future Improvements
- **Knowledge Graph Visualization**: Add a script to visualize the extracted knowledge graph using `NetworkX` and `pyvis`.
- **Web Interface**: Build a simple web app with `Streamlit` or `Gradio` to allow users to upload a PDF and view the extraction results interactively.
- **Quantitative Evaluation**: Develop a script to evaluate extraction accuracy against a ground-truth dataset.
- **Expanded Agent Support**: Add more agents, such as local models via `Ollama` or other cloud providers.
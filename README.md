# GeoMind Extractor 🧠

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-orange)](https://pydantic-docs.helpmanual.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GeoMind Extractor** is an AI-powered pipeline that extracts structured data, tables, and builds knowledge graphs from geological PDF documents. It leverages advanced Large Language Model (LLM) techniques to transform unstructured scientific papers into machine-readable knowledge.

This project goes beyond simple data extraction by implementing a robust, efficient, and intelligent processing workflow, making it a powerful tool for research automation and knowledge discovery.

## ✨ Core Features

This project showcases a range of advanced capabilities for building sophisticated, production-ready AI agents.

### 🧠 Advanced Prompt Engineering
- **Modular & Role-Based Prompts**: Specialized prompts for different tasks (metadata, table, and knowledge graph extraction), each defining a clear role for the AI agent.
- **Chain-of-Thought (CoT) Guidance**: Prompts are structured with step-by-step instructions, guiding the LLM through a logical reasoning process to improve accuracy on complex tasks.

### 🛡️ Robust Output Handling
- **Pydantic-Powered Validation**: All LLM outputs are strictly validated against Pydantic models (`src/models.py`), ensuring data integrity and structure.
- **Self-Correction Loop**: If an LLM output fails validation (e.g., invalid JSON, incorrect schema), the system automatically sends the error back to the LLM as feedback, asking it to "self-correct" its response. This significantly increases the reliability of data extraction.

### ⚡ Efficient Automation Pipeline
- **Intelligent Semantic Chunking**: Instead of naive text splitting, the pipeline first chunks documents by paragraph (`src/pdf_processor.py`). This preserves semantic context, providing higher-quality input to the LLM.
- **API Caching**: All calls to the LLM are cached in the `.cache/` directory. This drastically reduces costs and speeds up development by avoiding redundant API calls for the same content.

### 🕸️ Knowledge Graph Construction
- **Entity & Relationship Extraction**: The pipeline identifies key geological entities (`LOCATION`, `MINERAL`, etc.) and the relationships between them (`CONTAINS`, `LOCATED_IN`).
- **Structured Knowledge Output**: The extracted knowledge is structured as a graph (a list of nodes and edges), ready to be loaded into graph databases like Neo4j or visualized with libraries like NetworkX.

## ⚙️ How It Works

The pipeline follows these steps for each PDF document:

1.  **Full-Text Extraction**: The entire text content is extracted from the PDF.
2.  **Semantic Chunking**: The text is split into meaningful paragraphs (chunks).
3.  **Multi-Task Extraction (with Caching & Self-Correction)**:
    -   **Metadata**: The first chunk (usually the abstract) is used to extract metadata.
    -   **Knowledge Graph**: The first few chunks are used to build a knowledge graph of entities and relationships.
    -   **Tables**: The entire PDF is analyzed to find and extract the most significant table.
4.  **Structured Output**: All extracted information is compiled into a single, clean JSON file in the `data/processed` directory.

## 📂 Project Structure

```
GeoMind-Extractor/
├── .cache/               # Stores API call cache to reduce costs
├── README.md
├── requirements.txt
├── .env                  # For storing API Keys
├── data/
│   ├── finetune_dataset/ # (Future) Data for model fine-tuning
│   ├── processed/        # Processed JSON outputs
│   └── raw/              # Raw input PDFs
├── notebooks/
│   └── 1_Data_Exploration.ipynb # For exploring the extracted data
├── prompts/              # Advanced prompt templates for the LLM
│   ├── extract_entities.md
│   ├── extract_metadata.md
│   └── extract_table.md
└── src/                  # Source code
    ├── __init__.py
    ├── agent_interaction.py # Handles LLM calls, caching, and self-correction
    ├── main_pipeline.py     # Main executable pipeline
    ├── models.py            # Pydantic models for data validation
    └── pdf_processor.py     # Handles PDF parsing and semantic chunking
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- An API key for your language model provider (e.g., Google, OpenAI)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/GeoMind-Extractor.git
    cd GeoMind-Extractor
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
4.  **Configure Environment:**
    Create a `.env` file in the root directory and add your API key:
    ```
    GOOGLE_API_KEY="your_api_key_here"
    ```

## 💡 Future Improvements
- **Knowledge Graph Visualization**: Add a script to visualize the extracted knowledge graph using `NetworkX` and `pyvis`.
- **Database Integration**: Store the extracted structured data and graph relationships in a proper database (e.g., SQLite, PostgreSQL, or Neo4j).
- **Web Interface**: Build a simple web app with `Streamlit` or `Gradio` to allow users to upload a PDF and view the extraction results interactively.
- **Quantitative Evaluation**: Develop a script to evaluate extraction accuracy against a ground-truth dataset.
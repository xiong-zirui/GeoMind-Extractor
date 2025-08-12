from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict, Any

class ExtractedMetadata(BaseModel):
    """
    Defines the structure for metadata extracted from a document.
    """
    title: Optional[str] = Field(None, description="The title of the document.")
    authors: Optional[List[str]] = Field(None, description="A list of authors of the document.")
    publication_year: Optional[int] = Field(None, description="The year the document was published.")
    keywords: Optional[List[str]] = Field(None, description="A list of keywords associated with the document.")
    confidence_score: float = Field(..., ge=0, le=1, description="The model's confidence in the accuracy of the extracted metadata (0.0 to 1.0).")
    raw_text: str = Field(..., description="The raw text from which the metadata was extracted.")

class TableRow(BaseModel):
    """
    Represents a single row in an extracted table, allowing for flexible column structures.
    """
    row_data: Dict[str, Any] = Field(..., description="A dictionary representing the row's data, with column headers as keys.")

class ExtractedTable(BaseModel):
    """
    Defines the structure for a table extracted from a document.
    """
    table_name: str = Field(..., description="A descriptive name for the table.")
    columns: List[str] = Field(..., description="An ordered list of column headers.")
    data: List[TableRow] = Field(..., description="The table data, represented as a list of rows.")
    confidence_score: float = Field(..., ge=0, le=1, description="The model's confidence in the accuracy of the extracted table (0.0 to 1.0).")
    raw_text: str = Field(..., description="The raw text from which the table was extracted.")

class MapAnalysis(BaseModel):
    """
    Defines the structure for the analysis of a map image.
    """
    map_description: str = Field(..., description="A detailed description of the map's content and features.")
    geographic_area: Optional[str] = Field(None, description="The geographic area or location depicted in the map.")
    geological_features: List[str] = Field(..., description="A list of key geological features identified on the map.")
    confidence_score: float = Field(..., ge=0, le=1, description="The model's confidence in the accuracy of the map analysis (0.0 to 1.0).")

# --- Knowledge Graph Models ---

class Entity(BaseModel):
    """
    Represents a single named entity in the knowledge graph.
    """
    name: str = Field(..., description="The name of the entity (e.g., 'Nevada', 'Gold').")
    type: str = Field(..., description="The type of the entity (e.g., 'LOCATION', 'MINERAL').")

class Relationship(BaseModel):
    """
    Represents a relationship between two entities in the knowledge graph.
    """
    source: str = Field(..., description="The name of the source entity.")
    target: str = Field(..., description="The name of the target entity.")
    type: str = Field(..., description="The type of the relationship (e.g., 'CONTAINS', 'LOCATED_IN').")

class KnowledgeGraph(BaseModel):
    """
    Defines the structure for an extracted knowledge graph.
    """
    entities: List[Entity] = Field(..., description="A list of all identified entities.")
    relationships: List[Relationship] = Field(..., description="A list of all identified relationships between entities.")
    confidence_score: float = Field(..., ge=0, le=1, description="The model's confidence in the accuracy of the extracted graph (0.0 to 1.0).")

class Document(BaseModel):
    """
    The root model representing a single processed document and all its extracted data.
    """
    source_file: str = Field(..., description="The name of the original source file (e.g., 'report.pdf').")
    processing_timestamp_utc: str = Field(..., description="The UTC timestamp of when the document was processed.")
    full_text: Optional[str] = Field(None, description="The full text extracted from the document.")
    metadata: Optional[ExtractedMetadata] = Field(None, description="The extracted metadata from the document.")
    extracted_tables: List[ExtractedTable] = Field([], description="A list of tables extracted from the document.")
    knowledge_graph: Optional[KnowledgeGraph] = Field(None, description="The knowledge graph extracted from the document.")
    image_analysis: List[MapAnalysis] = Field([], description="A list of analyses for images found in the document.")

class ExtractionError(BaseModel):
    """
    A model to represent an error during the extraction process.
    """
    error_message: str
    original_prompt: str
    failed_response: str

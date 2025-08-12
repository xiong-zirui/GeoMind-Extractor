import logging
from neo4j import GraphDatabase, basic_auth
from src.models import KnowledgeGraph

class Neo4jLoader:
    def __init__(self, uri, user, password, database=None):
        """
        Initializes the Neo4jLoader with connection details.
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
            self.database = database
            logging.info("Successfully connected to Neo4j.")
        except Exception as e:
            logging.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """
        Closes the Neo4j driver connection.
        """
        if self.driver:
            self.driver.close()
            logging.info("Neo4j connection closed.")

    def load_graph(self, knowledge_graph: KnowledgeGraph, source_document: str):
        """
        Loads a knowledge graph into Neo4j, linking it to a source document.
        """
        if not isinstance(knowledge_graph, KnowledgeGraph):
            logging.error("Invalid data type. Expected KnowledgeGraph object.")
            return

        with self.driver.session(database=self.database) as session:
            # Step 1: Create or merge the source document node
            session.execute_write(self._create_document_node, source_document)

            # Step 2: Create or merge all entities
            for entity in knowledge_graph.entities:
                session.execute_write(self._create_entity_node, entity)

            # Step 3: Create all relationships
            for rel in knowledge_graph.relationships:
                session.execute_write(self._create_relationship, rel)
            
            # Step 4: Link all entities to the source document
            for entity in knowledge_graph.entities:
                session.execute_write(self._link_entity_to_document, entity.name, source_document)

        logging.info(f"Successfully loaded knowledge graph from '{source_document}' into Neo4j.")

    @staticmethod
    def _create_document_node(tx, document_name):
        """
        Creates or merges a Document node.
        """
        query = (
            "MERGE (d:Document {name: $name})"
            "ON CREATE SET d.createdAt = timestamp()"
        )
        tx.run(query, name=document_name)

    @staticmethod
    def _create_entity_node(tx, entity):
        """
        Creates or merges an Entity node with a specific label (type).
        """
        # Sanitize label to be valid in Cypher
        sanitized_label = ''.join(filter(str.isalnum, entity.type.capitalize()))
        
        query = (
            f"MERGE (e:{sanitized_label} {{name: $name}}) "
            "ON CREATE SET e.type = $type"
        )
        tx.run(query, name=entity.name, type=entity.type)

    @staticmethod
    def _create_relationship(tx, rel):
        """
        Creates a relationship between two existing entity nodes.
        """
        # Relationships in Cypher cannot be parameterized in the same way as labels.
        # It's generally safer to have a predefined set of relationship types.
        # We will use the relationship type from the data directly, but ensure it's sanitized.
        sanitized_rel_type = rel.type.upper().replace(" ", "_")

        query = (
            "MATCH (source {name: $source_name}), (target {name: $target_name}) "
            f"MERGE (source)-[r:{sanitized_rel_type}]->(target)"
        )
        tx.run(query, source_name=rel.source, target_name=rel.target)

    @staticmethod
    def _link_entity_to_document(tx, entity_name, document_name):
        """
        Creates a 'MENTIONED_IN' relationship from an entity to its source document.
        """
        query = (
            "MATCH (e {name: $entity_name}), (d:Document {name: $document_name}) "
            "MERGE (e)-[:MENTIONED_IN]->(d)"
        )
        tx.run(query, entity_name=entity_name, document_name=document_name)

    def clear_database(self):
        """
        Deletes all nodes and relationships from the database.
        USE WITH CAUTION.
        """
        logging.warning("Clearing the entire Neo4j database.")
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._delete_all)

    @staticmethod
    def _delete_all(tx):
        """
        Transaction function to delete all nodes and relationships.
        """
        query = "MATCH (n) DETACH DELETE n"
        tx.run(query)

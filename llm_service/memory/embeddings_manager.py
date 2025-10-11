"""
Embeddings Manager - Qdrant Vector Store using LangChain
Stores and retrieves embeddings using OpenAI + Qdrant.
"""

import os
import logging
import uuid
from typing import List, Dict, Any, Optional

from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

logger = logging.getLogger(__name__)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "unify_memory"
EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_SIZE = 1536

class EmbeddingsManager:
    """Manages vector embeddings with Qdrant using LangChain."""
    
    def __init__(self, qdrant_url: str = QDRANT_URL):
        """Initialize Qdrant client and embeddings."""
        self.qdrant_url = qdrant_url
        self.collection_name = COLLECTION_NAME
        self.client = QdrantClient(url=qdrant_url)
        
        # Initialize LangChain OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        logger.info(f"Initialized EmbeddingsManager with Qdrant at {qdrant_url}")
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}", exc_info=True)
            raise
    
    def store_embedding(
        self,
        text: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> str:
        """
        Store text and its embedding in Qdrant using LangChain.
        
        Args:
            text: Text to embed and store
            metadata: Metadata to store with the text
            doc_id: Optional document ID
            
        Returns:
            Document ID (generated or provided)
        """
        try:
            if not text.strip():
                logger.warning("Empty text provided, skipping storage")
                return doc_id or ""
            
            # Store original doc_id
            original_doc_id = doc_id or str(uuid.uuid4())
            
            # Generate UUID for Qdrant (required format)
            if doc_id:
                # Convert string ID to UUID v5 (deterministic)
                qdrant_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))
            else:
                # Generate random UUID
                qdrant_uuid = str(uuid.uuid4())
            
            # Use LangChain's Qdrant vectorstore for storage
            vectorstore = Qdrant(
                client=self.client,
                collection_name=self.collection_name,
                embeddings=self.embeddings
            )
            
            # Add metadata with original doc_id
            full_metadata = {
                "doc_id": original_doc_id,
                **metadata
            }
            
            # Store using LangChain with UUID
            vectorstore.add_texts(
                texts=[text],
                metadatas=[full_metadata],
                ids=[qdrant_uuid]  # Use UUID format
            )
            
            logger.info(f"Stored embedding for document: {original_doc_id} (Qdrant UUID: {qdrant_uuid})")
            return original_doc_id
            
        except Exception as e:
            logger.error(f"Error storing embedding: {e}", exc_info=True)
            raise
    
    def query_similar(
        self,
        query_text: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query similar documents using semantic search.
        
        Args:
            query_text: Text to search for
            top_k: Number of results to return
            metadata_filter: Optional metadata filters
            
        Returns:
            List of similar documents with scores
        """
        try:
            if not query_text.strip():
                logger.warning("Empty query text provided")
                return []
            
            # Generate embedding for query using LangChain
            query_vector = self.embeddings.embed_query(query_text)
            
            # Search using raw Qdrant client (more reliable than LangChain wrapper)
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )
            
            # Format results
            formatted_results = []
            for hit in search_results:
                # Extract text from either 'text' field or 'page_content' (LangChain format)
                text = hit.payload.get("text", "") or hit.payload.get("page_content", "")
                
                formatted_results.append({
                    "id": hit.payload.get("doc_id", str(hit.id)),
                    "text": text,
                    "score": float(hit.score),
                    "metadata": hit.payload
                })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying similar documents: {e}", exc_info=True)
            return []
    
    def delete_embedding(self, doc_id: str) -> bool:
        """
        Delete an embedding by document ID.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[doc_id]
            )
            logger.info(f"Deleted embedding for document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting embedding: {e}", exc_info=True)
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": "ready"
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "name": self.collection_name,
                "status": "error",
                "error": str(e)
            }

# Singleton instance
_embeddings_manager = None

def get_embeddings_manager() -> EmbeddingsManager:
    """Get or create singleton EmbeddingsManager instance."""
    global _embeddings_manager
    if _embeddings_manager is None:
        _embeddings_manager = EmbeddingsManager()
    return _embeddings_manager

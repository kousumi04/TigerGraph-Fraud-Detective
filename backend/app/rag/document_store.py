# backend/app/rag/document_store.py
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class PolicyDocumentStore:
    """
    Local vector store for Fraud Policy, Patterns, and Regulatory documents.
    Ensures the LLM relies on factual, authoritative guidelines rather than its internal weights.
    """
    def __init__(self, persist_directory: str = "artifacts/chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.collection_name = "fraud_guidance"
        
        # Initialize or load Chroma vector store
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def ingest_documents(self, documents: List[Document]):
        """Indexes policy and regulatory documents."""
        if documents:
            self.vector_store.add_documents(documents)
            logger.info(f"Ingested {len(documents)} documents into vector store.")

    def retrieve_guidance(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves the most relevant policy chunks for a given investigation query.
        """
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "similarity_score": round(float(score), 4)
            })
            
        return formatted_results
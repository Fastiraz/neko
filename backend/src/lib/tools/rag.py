#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import ollama
import re
from time import time


class RAG:
    def __init__(self, vectordb: str = "vectordb") -> None:
        self.datasets = []
        self.documents = []
        self.chunks = []
        self.embed_dim = None
        self.metadata = []
        self.client = chromadb.PersistentClient(
            path=vectordb,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(name="docs")
        self.system_prompt = """You are Eliot, a helpful assistant that answers questions based on the provided context.
Your goal is to provide accurate.
If the context doesn't contain enough information to answer the question fully:
1. Use what is available in the context
2. Clearly indicate what parts of your response are based on the context
3. If you don't have enough information use your own knowledge for a complete answer
Keep your responses clear, concise, and directly relevant to the user's question."""


    def load(self, directory: str = "datasets", allowed_extensions: List[str] = None) -> List[str]:
        """
        Recursively loads files from a directory.

        Args:
          directory (str): Path to the datasets directory.
          allowed_extensions(List[str]): List of allowed extensions.

        Returns:
          List[str]: Loaded text from the datasets.
        """
        if allowed_extensions is None:
            allowed_extensions = [".md", ".txt", ".c", ".cpp", ".py", ".asm"]
        self.datasets = []
        self.documents = []
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in allowed_extensions):
                    path = os.path.join(root, file)
                    self.datasets.append(path)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self.documents.append(content)
                            print(f"Loaded: {path} ({len(content)} chars)")
                    except Exception as e:
                        print(f"Failed to read {path}: {e}")
        print(f"Loaded {len(self.documents)} documents")
        return self.documents


    def chunk(self, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Splits documents into overlapping chunks with improved chunking strategy.

        Args:
          chunk_size (int): Size of each chunks.
          overlap (int):

        Returns:
          List[str]: Chunked text.
        """
        self.chunks = []
        self.metadata = []
        for i, doc in enumerate(self.documents):
            # Try to split on paragraph boundaries first
            paragraphs = re.split(r'\n\s*\n', doc)
            current_chunk = ""
            for para in paragraphs:
                # If paragraph is too long, split it further
                if len(para) > chunk_size:
                    # Try to split on sentence boundaries
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) <= chunk_size:
                            current_chunk += sentence + " "
                        else:
                            if current_chunk:
                                self.chunks.append(current_chunk.strip())
                                self.metadata.append({"source": self.datasets[i] if i < len(self.datasets) else "unknown"})
                            # If sentence is longer than chunk_size, use simple chunking
                            if len(sentence) > chunk_size:
                                start = 0
                                while start < len(sentence):
                                    end = min(start + chunk_size, len(sentence))
                                    self.chunks.append(sentence[start:end].strip())
                                    self.metadata.append({"source": self.datasets[i] if i < len(self.datasets) else "unknown"})
                                    start += chunk_size - overlap
                            else:
                                current_chunk = sentence + " "
                else:
                    # Add paragraph if it fits
                    if len(current_chunk) + len(para) <= chunk_size:
                        current_chunk += para + "\n\n"
                    else:
                        if current_chunk:
                            self.chunks.append(current_chunk.strip())
                            self.metadata.append({"source": self.datasets[i] if i < len(self.datasets) else "unknown"})
                        current_chunk = para + "\n\n"
            # Add the last chunk
            if current_chunk:
                self.chunks.append(current_chunk.strip())
                self.metadata.append({"source": self.datasets[i] if i < len(self.datasets) else "unknown"})
        print(f"Created {len(self.chunks)} chunks from {len(self.documents)} documents")
        return self.chunks


    def embedding(self, text: str) -> List[float]:
        """
        Get a single embedding vector from Ollama.

        Args:
          text (str): The text to get the embeddings from.

        Returns:
          List[float]: A list of embeddings.
        """
        try:
            result = ollama.embed(
                model=os.environ.get('EMBED_MODEL', 'mxbai-embed-large:latest').strip().strip('"'),
                input=text
            )
            embeddings = result["embeddings"]
            return embeddings[0] if isinstance(embeddings[0], list) else embeddings
        except Exception as e:
            print(f"Embedding failed: {e}")
            return []


    def vector_store(self) -> None:
        """
        Stores document chunks in the vector DB with metadata.
        """
        start = time()
        print("Embedding and storing chunks...")
        # Process in smaller batches to avoid memory issues
        batch_size = 50
        for i in range(0, len(self.chunks), batch_size):
            batch_chunks = self.chunks[i:i+batch_size]
            batch_metadata = self.metadata[i:i+batch_size]
            # batch_ids = [str(i+j) for j in range(len(batch_chunks))]
            ids, embeddings, documents, metadatas = [], [], [], []
            for j, chunk in enumerate(batch_chunks):
                idx = i + j
                emb = self.embedding(chunk)
                if not emb:
                    print(f"Skipping chunk {idx} due to embedding failure")
                    continue
                if self.embed_dim is None:
                    self.embed_dim = len(emb)
                if len(emb) != self.embed_dim:
                    print(f"Skipping chunk {idx} due to dimension mismatch: {len(emb)} != {self.embed_dim}")
                    continue
                ids.append(str(idx))
                embeddings.append(emb)
                documents.append(chunk)
                metadatas.append(batch_metadata[j])
            if embeddings:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
            print(f"Processed {i+len(batch_chunks)}/{len(self.chunks)} chunks")
        print(f"Vector store ready. Stored {len(self.chunks)} chunks in {time() - start:.2f} seconds")


    def semantic_search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Perform semantic search using embeddings.

        Args:
          query (str): The search query.
          n_results (int): Number of results.

        Returns:
          Dict[str, Any]:
        """
        emb = self.embedding(query)
        if not emb:
            print("No embedding generated for query.")
            return {"documents": [], "scores": [], "metadatas": []}
        results = self.collection.query(
            query_embeddings=[emb],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return {
            "documents": results['documents'][0] if results and 'documents' in results else [],
            "scores": [1 - d for d in results['distances'][0]] if results and 'distances' in results else [],
            "metadatas": results['metadatas'][0] if results and 'metadatas' in results else []
        }


    def hybrid_search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Combine semantic search with keyword matching for better retrieval.

        Args:
          query (str): The search query.
          n_results (int): Number of results.

        Returns:
          Dict[str, Any]: A dictionary containing the following keys:
            - 'documents' (List[str]): The reranked documents based on hybrid scoring.
            - 'scores' (List[float]): Combined scores (semantic + keyword boost).
            - 'metadatas' (List[Dict]): Metadata associated with each document.
        """
        # Semantic search results
        semantic_results = self.semantic_search(query, n_results=n_results)
        # Simple keyword matching based on exact matches
        query_keywords = set(re.findall(r'\b\w+\b', query.lower()))
        # Rerank results based on keyword matches
        reranked_results = {"documents": [], "scores": [], "metadatas": []}
        for i, doc in enumerate(semantic_results["documents"]):
            doc_text = doc.lower()
            keyword_matches = sum(1 for kw in query_keywords if kw in doc_text)
            # Compute a combined score (semantic + keyword match boost)
            semantic_score = semantic_results["scores"][i] if i < len(semantic_results["scores"]) else 0
            combined_score = semantic_score + (keyword_matches * 0.05)  # Small boost per keyword match
            reranked_results["documents"].append(doc)
            reranked_results["scores"].append(combined_score)
            reranked_results["metadatas"].append(semantic_results["metadatas"][i] if i < len(semantic_results["metadatas"]) else {})
        # Sort by combined score
        sorted_indices = sorted(range(len(reranked_results["scores"])), key=lambda i: reranked_results["scores"][i], reverse=True)
        reranked_results["documents"] = [reranked_results["documents"][i] for i in sorted_indices]
        reranked_results["scores"] = [reranked_results["scores"][i] for i in sorted_indices]
        reranked_results["metadatas"] = [reranked_results["metadatas"][i] for i in sorted_indices]
        return reranked_results


    def retrieval(self, prompt: str) -> List[str]:
        """
        Enhanced retrieval function that uses hybrid search.

        Args:
          prompt (str): The user prompt

        Returns:
          List[str]: A list of revelant documents
        """
        results = self.hybrid_search(prompt, n_results=5)
        # Filter out low-relevance results (threshold can be adjusted)
        threshold = 0.6
        filtered_docs = []
        for i, doc in enumerate(results["documents"]):
            if i < len(results["scores"]) and results["scores"][i] >= threshold:
                # Add source info if available
                source_info = ""
                if i < len(results["metadatas"]) and results["metadatas"][i] and "source" in results["metadatas"][i]:
                    source = results["metadatas"][i]["source"]
                    source_info = f"\n[Source: {os.path.basename(source)}]"
                filtered_docs.append(doc + source_info)
        return filtered_docs

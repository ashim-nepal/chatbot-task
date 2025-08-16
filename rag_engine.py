from typing import List, Tuple # all the required inputs
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

_embedding_model = None # vatiable to store model

# Getting embedding model
def get_embedder():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2") # Sentence transformer model
    return _embedding_model

# Function to break long texts into chunks
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    text = text.replace("\n", " ").strip() # Cleaning spaces and new lines
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+chunk_size] # Breaking texts into chunks
        chunks.append(chunk)
        i += max(1, chunk_size - overlap)
    return chunks

# Function to create a FAISS index for fast retrival
def build_faiss(chunks: List[str]):
    emb = get_embedder()
    vecs = emb.encode(chunks, convert_to_numpy=True, normalize_embeddings=True) # Convertinf chucks into vectors
    dim = vecs.shape[1]
    index = faiss.IndexFlatIP(dim) # Creting a faiss index
    index.add(vecs.astype(np.float32))
    return index, vecs, chunks

# Function to retrive the faiss index
def retrieve(query: str, index, chunks: List[str], top_k: int = 4) -> List[Tuple[int, float, str]]:
    emb = get_embedder()
    qv = emb.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32) # Comnverting query into vector
    D, I = index.search(qv, top_k) # Searches index for most similar chunks 
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx == -1:
            continue
        results.append((int(idx), float(score), chunks[idx])) # Append the index score and retrived chunk to results
    return results


# BY ASHIM NEPAL
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

def load_faiss_index(index_path):
    # Load the FAISS index from the binary file
    index = faiss.read_index(index_path)
    return index

def load_chunks(json_path):
    # Load the chunks from the JSON file
    with open(json_path, 'r') as f:
        chunks_data = json.load(f)
    return chunks_data["chunks"]

def embed_query(query, model):
    # Embed the query using SentenceTransformer
    query_embedding = model.encode([query])
    return query_embedding

def search_faiss(query, top_k=10):
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Paths to FAISS index and JSON file
    index_path = "../data/faiss_index.bin"
    json_path = "../data/chunks.json"
    
    # Load FAISS index and chunks
    index = load_faiss_index(index_path)
    chunks_data = load_chunks(json_path)
    # Embed the query
    query_embedding = embed_query(query, model)
    
    # Perform the search on the FAISS index
    distances, indices = index.search(np.array(query_embedding).astype(np.float32), top_k)
    
    # Retrieve corresponding chunks based on FAISS search indices
    retrieved_chunks = []
    for idx in indices[0]:
        chunk = next((item for item in chunks_data if item["id"] == idx), None)
        if chunk:
            retrieved_chunks.append(chunk["text"])
    
    return retrieved_chunks, distances[0]

# Example usage
if __name__ == "__main__":

    # Query to search for
    query = "Apple net income"
    
    # Search in FAISS
    retrieved_chunks, distances = search_faiss(query)
    
    print(f"Query: {query}")
    print(f"Top {len(retrieved_chunks)} retrieved chunks:")
    for i, chunk in enumerate(retrieved_chunks):
        print(f"{i+1}: {chunk} (Distance: {distances[i]:.4f})")

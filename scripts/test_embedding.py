import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load a Sentence Transformer model (optimized for similarity search)
model = SentenceTransformer("all-MiniLM-L6-v2")  # Small & fast, but effective

# Sample text chunks
chunks = [
    "This is the first document. It contains some interesting information.",
    "Here is the second document. It is about something completely different.",
    "This third document has more details that we need to analyze.",
    "The zebra is a wild animal"
]

# Compute embeddings for text chunks
embeddings = model.encode(chunks, normalize_embeddings=True)  # Normalized for cosine similarity

# Convert to float32 for FAISS
embedding_matrix = embeddings.astype('float32')

# Create a FAISS index for cosine similarity
embedding_dim = embedding_matrix.shape[1]  # Should be 384 for MiniLM
index = faiss.IndexFlatIP(embedding_dim)

# Add normalized embeddings to FAISS
index.add(embedding_matrix)

# Function to search FAISS index
def search_faiss(query, index, k=3):
    query_embedding = model.encode([query], normalize_embeddings=True).astype('float32')
    D, I = index.search(query_embedding, k)  # FAISS search
    return D, I

# Example query
query = "Tell me about the first document"
distances, indices = search_faiss(query, index)

# Print results
print(f"Query: {query}")
print("\nTop 3 most similar chunks:")
for i, idx in enumerate(indices[0]):
    print(f"Rank {i+1} (Score: {distances[0][i]:.4f}): {chunks[idx]}")

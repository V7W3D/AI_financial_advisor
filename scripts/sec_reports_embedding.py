from glob import glob
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
from sentence_transformers import SentenceTransformer
import json

files = glob("../data/sec_reports/*.pdf")

pages = []
for f in files:
    reader = PdfReader(f)
    for i, page in enumerate(reader.pages):
        pages.append(page.extract_text().strip())

splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=100)

chunks_list = []
for p in pages: 
    chunks_list.append(splitter.split_text(p))

chunks = [item  for sublist in chunks_list for item in sublist]

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(chunks, normalize_embeddings=True)

# Convert to float32 for FAISS
embedding_matrix = embeddings.astype('float32')

# Create a FAISS index for cosine similarity
embedding_dim = embedding_matrix.shape[1]  # Should be 384 for MiniLM
index = faiss.IndexFlatIP(embedding_dim)

# Add normalized embeddings to FAISS
index.add(embedding_matrix)

# Write FAISS index and text chunks
faiss.write_index(index, "../data/faiss_index.bin")

structured_chunks = [{"id": i, "text": chunk} for i, chunk in enumerate(chunks)]
with open("../data/chunks.json", "w") as f:
    json.dump({"chunks": structured_chunks}, f, indent=4)
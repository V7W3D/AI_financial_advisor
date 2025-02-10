import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from yfinance import Ticker
import os
import getpass

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

# FAISS RAG Agent
class RagAgent:
    def __init__(self, index_path, json_path):
        self.index_path = index_path
        self.json_path = json_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def load_faiss_index(self):
        return faiss.read_index(self.index_path)

    def load_chunks(self):
        with open(self.json_path, 'r') as f:
            chunks_data = json.load(f)
        return chunks_data["chunks"]

    def embed_query(self, query):
        return self.model.encode([query])

    def search_faiss(self, query, top_k=10):
        index = self.load_faiss_index()
        chunks_data = self.load_chunks()
        query_embedding = self.embed_query(query)

        distances, indices = index.search(np.array(query_embedding).astype(np.float32), top_k)
        retrieved_chunks = [next((item for item in chunks_data if item["id"] == idx), None) for idx in indices[0]]
        
        return [(chunk["text"], distances[i]) for i, chunk in enumerate(retrieved_chunks) if chunk is not None]

# yFinance Financial Data Agent
class YFinanceAgent:
    def __init__(self, ticker):
        self.ticker = ticker

    def get_quote_info(self, list_params):
        quote = Ticker(self.ticker).info
        result = {param: quote[param] for param in list_params if param in quote}
        return result

# Agent orchestrator
class AgentOrchestrator:
    def __init__(self, faiss_agent, yf_agent):
        self.faiss_agent = faiss_agent
        self.yf_agent = yf_agent

    def process_query(self, user_input):
        # Step 1: RAG-based retrieval from FAISS
        retrieved_chunks = self.faiss_agent.search_faiss(user_input)

        # Step 2: Check if any company-related information was retrieved
        company_name = self.extract_company_name(user_input)
        if company_name:
            # Get ticker symbol based on the company name
            ticker = self.get_ticker_from_company_name(company_name)
            yf_data = self.yf_agent.get_quote_info(["netIncome", "marketCap"])  # Modify params as needed
            return self.format_response(retrieved_chunks, yf_data)

        return self.format_response(retrieved_chunks)

    def extract_company_name(self, user_input):
        """Extract company name from user input (for simplicity, assume it's a direct match)"""
        company_names = ["Apple", "Microsoft", "Tesla", "Google"]  # Extend this list
        for company in company_names:
            if company.lower() in user_input.lower():
                return company
        return None

    def get_ticker_from_company_name(self, company_name):
        """Map company name to ticker (extend as needed)"""
        ticker_map = {"Apple": "AAPL", "Microsoft": "MSFT", "Tesla": "TSLA", "Google": "GOOG"}
        return ticker_map.get(company_name)

    def format_response(self, retrieved_chunks, yf_data=None):
        """Format the response combining both the retrieved chunks and financial data (if available)"""
        response = "Here is the information I found:\n"

        if retrieved_chunks:
            response += "\nTop Retrieved Information:\n"
            for i, (chunk, dist) in enumerate(retrieved_chunks):
                response += f"{i+1}: {chunk} (Distance: {dist:.4f})\n"

        if yf_data:
            response += "\nAdditional Financial Data:\n"
            for param, value in yf_data.items():
                response += f"{param}: {value}\n"

        return response


# Example usage
if __name__ == "__main__":
    # Initialize agents
    faiss_agent = RagAgent(index_path="../data/faiss_index.bin", json_path="../data/chunks.json")
    yf_agent = YFinanceAgent(ticker="AAPL")  # Example ticker for Apple
    orchestrator = AgentOrchestrator(faiss_agent, yf_agent)

    # User input query
    user_input = "What is Apple's net income?"

    # Process the query
    response = orchestrator.process_query(user_input)
    print(response)

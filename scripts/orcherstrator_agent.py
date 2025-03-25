import os
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI

from . import yfinance_search_agent
from . import sec_reports_retreival_agent

def create_orchestrator_agent(yfinance_agent, faiss_agent):
    """
    Create an orchestrator agent that manages multiple financial information retrieval agents.
    
    Returns:
        Agent: Initialized LangChain agent with multiple tools
    """
    try:
        # Load environment variables
        load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Create tools from existing agents
        tools = [
            Tool(
                name="StockQuoteTool",
                func=yfinance_agent.run,
                description="Retrieves current stock quote and financial metrics for companies"
            ),
            Tool(
                name="SECReportsTool",
                func=faiss_agent.run,
                description="Retrieves detailed financial information from SEC reports"
            )
        ]

        # Initialize LLM with a slightly lower temperature for more focused responses
        llm = ChatOpenAI(temperature=0.5)
        
        # Create prompt template
        prompt_template = """
        You are an advanced financial research assistant. Your goal is to provide comprehensive 
        financial insights by leveraging multiple information sources:
        1. Real-time stock quotes and metrics
        2. Detailed SEC report analysis

        When a query is received:
        - Use StockQuoteTool directly with the full user query for immediate financial metrics
        - Use SECReportsTool directly with the full user query for in-depth contextual information
        - Synthesize insights from both sources to provide a holistic answer

        Please return the synthetized insights in your response.

        User Question: {input}
        """

        # Initialize orchestrator agent
        agent = initialize_agent(
            tools,
            llm,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            agent_kwargs={
                "prefix": prompt_template
            },
            handle_parsing_errors=True
        )
        return agent

    except Exception as e:
        raise Exception(f"Failed to create orchestrator agent: {str(e)}")

def main():
    """Main function to demonstrate orchestrator agent usage."""
    query = "Should I Invest in Microsoft"

    try:
        search_agent = yfinance_search_agent.create_agent()
        faiss_agent = sec_reports_retreival_agent.create_agent()
        orchestrator = create_orchestrator_agent(search_agent, faiss_agent)
        
        print(f"\nQuery: {query}")
        response = orchestrator.run(input=query)
        print(f"Response: {response}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
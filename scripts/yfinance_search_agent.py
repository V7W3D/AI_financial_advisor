from typing import Dict
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
from yfinance import Ticker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Type definitions
ParameterMap = Dict[str, str]
CompanyMap = Dict[str, str]

# Financial parameters mapping
PARAMETER_MAP: ParameterMap = {
    "ebitda margin": "ebitdaMargins",
    "market cap": "marketCap",
    "previous close": "previousClose",
    "current price": "currentPrice",
}

# Company to ticker mapping
COMPANY_TICKER_MAP: CompanyMap = {
    "Apple": "AAPL",
    "Google": "GOOG",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
}

def extract_ticker_and_param(user_input: str) -> dict:
    """
    Extract the company name and financial parameter from the user's query.
    
    Args:
        user_input (str): The user's query string
        
    Returns:
        dict: Dictionary containing ticker and parameter
    """
    ticker = None
    param = None
    
    # Convert input to lowercase once for efficiency
    user_input_lower = user_input.lower()
    
    # Find company name
    for company_name in COMPANY_TICKER_MAP:
        if company_name.lower() in user_input_lower:
            ticker = COMPANY_TICKER_MAP[company_name]
            break
    
    # Find parameter
    for key in PARAMETER_MAP:
        if key.lower() in user_input_lower:
            param = PARAMETER_MAP[key]
            break

    return {"ticker": ticker, "param": param}

def get_quote_info(query: str) -> str:
    """
    Get stock quote information based on extracted ticker and parameter.
    
    Args:
        query (str): The original query string
        
    Returns:
        str: Formatted response with the requested information
    """
    try:
        # Extract ticker and parameter from query
        extracted = extract_ticker_and_param(query)
        ticker = extracted["ticker"]
        param = extracted["param"]
        
        if not ticker or not param:
            return "Could not extract ticker or parameter from query."
        
        # Get quote information
        quote = Ticker(ticker).info
        
        if param not in quote:
            return f"Parameter {param} not found for {ticker}"
            
        value = quote[param]

        return f"The {param} for {ticker} is {value}"
        
    except Exception as e:
        return f"Error retrieving quote information: {str(e)}"

def create_agent():
    """
    Create and run an agent for handling financial queries.
    
    Returns:
        Agent: Initialized LangChain agent
    """
    try:
        # Initialize tools
        tools = [
            Tool(
                name="get_quote",
                func=get_quote_info,
                description="Gets stock quote information for a given query"
            )
        ]
        
        llm = ChatOpenAI(temperature=0.7)
        
        # Create prompt template
        prompt_template = """
        You are a helpful financial assistant. Your task is to help users get financial information about companies.
        When users ask about specific financial metrics, use the get_quote tool directly with their query.
        
        User Question: {input}
        """

        # Initialize agent
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
        raise Exception(f"Failed to create agent: {str(e)}")

def main():
    """Main function to demonstrate usage."""
    user_input = "give me some information about Microsoft market cap"
    try:
        agent = create_agent()
        response = agent.run(input=user_input)
        print(response)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
from typing import Optional, List, Dict, Tuple
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
from yfinance_tools import yfinance_tools
from dotenv import load_dotenv
import os
from logging import getLogger, basicConfig, INFO

# Set up logging
basicConfig(level=INFO)
logger = getLogger(__name__)

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
    "current price": "regularMarketPrice",
    # Add more mappings as needed
}

# Company to ticker mapping
COMPANY_TICKER_MAP: CompanyMap = {
    "Apple": "AAPL",
    "Google": "GOOG",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    # Add more companies as needed
}

def extract_company_and_param(user_input: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract the company name and financial parameter from the user's query.
    
    Args:
        user_input (str): The user's query string
        
    Returns:
        Tuple[Optional[str], Optional[str]]: Tuple containing company name and parameter
    """
    company = None
    param = None
    
    # Convert input to lowercase once for efficiency
    user_input_lower = user_input.lower()
    
    # Find company name
    for company_name in COMPANY_TICKER_MAP:
        if company_name.lower() in user_input_lower:
            company = company_name
            break
    
    # Find parameter
    for key in PARAMETER_MAP:
        if key.lower() in user_input_lower:
            param = PARAMETER_MAP[key]
            break

    return company, param

class QuoteInfoTool:
    """Tool for fetching stock quote information."""
    
    def __init__(self, yfinance_tool: yfinance_tools, list_params: List[str]):
        """
        Initialize the QuoteInfoTool.
        
        Args:
            yfinance_tool (yfinance_tools): YFinance tools instance
            list_params (List[str]): List of parameters to fetch
        """
        self.yfinance_tool = yfinance_tool
        self.list_params = list_params

    def __call__(self, query: str) -> str:
        """
        Run the tool to fetch stock information.
        
        Args:
            query (str): The query string (not used but required by Tool interface)
            
        Returns:
            str: The fetched stock information
        """
        try:
            return self.yfinance_tool.get_quote_info(self.list_params)
        except Exception as e:
            logger.error(f"Error fetching quote info: {str(e)}")
            return f"Error fetching quote information: {str(e)}"

def create_tool(yfinance_tool: yfinance_tools, list_params: List[str]) -> Tool:
    """Create a LangChain Tool instance for the quote info tool."""
    quote_tool = QuoteInfoTool(yfinance_tool, list_params)
    return Tool(
        name="quote_info_tool",
        func=quote_tool,
        description="Fetches stock quote information for a given ticker."
    )

def create_agent_for_query(user_input: str) -> str:
    """
    Create and run an agent for handling financial queries.
    
    Args:
        user_input (str): The user's query string
        
    Returns:
        str: The agent's response
    """
    try:
        company, param = extract_company_and_param(user_input)
        
        if not company or not param:
            return "Could not extract company or financial parameter from the input. Please try again with a clearer query."

        ticker = COMPANY_TICKER_MAP.get(company)
        if not ticker:
            return f"Sorry, I don't have ticker information for {company}. Please try with a different company."

        # Initialize tools and LLM
        financial_tool = yfinance_tools(ticker)
        tool = create_tool(financial_tool, [param])
        tools = [tool]
        llm = ChatOpenAI(temperature=0.7)
        
        # Create prompt template
        prompt_template = """
        You are a helpful financial assistant. You have access to the following tools:

        {tools}

        Use these tools to answer the user's question about {company}'s {param}.
        If you encounter any errors or need external information, use the appropriate tools.
        
        User Question: {input}
        """
        
        prompt = PromptTemplate(
            input_variables=["tools", "company", "param", "input"],
            template=prompt_template
        )
        
        # Initialize agent with callback for token tracking
        with get_openai_callback() as cb:
            agent = initialize_agent(
                tools,
                llm,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
            response = agent.run(
                input=user_input,
                tools=tools,
                company=company,
                param=param
            )
            logger.info(f"Total tokens used: {cb.total_tokens}")
            
        return response

    except Exception as e:
        logger.error(f"Error in create_agent_for_query: {str(e)}")
        return f"An error occurred while processing your request: {str(e)}"

def main():
    """Main function to demonstrate usage."""
    user_input = "What is Apple's ebitda margin?"
    try:
        response = create_agent_for_query(user_input)
        print(f"Query: {user_input}")
        print(f"Response: {response}")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
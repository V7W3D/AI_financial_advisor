from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
import yfinance_tools
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

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
                func=yfinance_tools.get_quote_info,
                description="Gets stock quote information for a given query"
            )
        ]
        
        llm = ChatOpenAI(temperature=0.7)
        
        # Create prompt template
        prompt_template = """
        You are a helpful financial assistant. Your task is to help users get financial information about companies.
        When users ask about specific financial metrics, use the get_quote tool by providing it the yfinance ticker
        and a list of yfinance quote keys corresponding the user's query. 
        
        Example of parameters for get_quote call : MSFT, MarketCap, dividendYield, previousClose

        User Query: {input}
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
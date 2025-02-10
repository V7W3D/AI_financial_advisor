from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
import sec_reports_retrieval
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
    Create an agent to perferom RAG on FAISS database.
    
    Returns:
        Agent: Initialized LangChain agent
    """
    try:

        tools = [
            Tool(
                name="RetrieveDocs",
                func=sec_reports_retrieval.search_faiss,
                description="Retrieves relevant documents from SEC reports"
            )
        ]

        llm = ChatOpenAI(temperature=0.7)
        
        # Create prompt template
        prompt_template = """
        You are a helpful financial assistant. Your task is to help users get financial information about companies.
        Use the RetrieveDocs tool directly with their full query in order to retreive more context from SEC reports.

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
    user_input = "should I invest in Microsoft"
    try:
        agent = create_agent()
        response = agent.run(input=user_input)
        print(response)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
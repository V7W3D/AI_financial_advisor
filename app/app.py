import streamlit as st
import sys
import os

# Add the directory containing your agents to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the orchestrator and agents
from scripts import orcherstrator_agent
from scripts import yfinance_search_agent
from scripts import sec_reports_retreival_agent

def initialize_agents():
    """Initialize the search and SEC report agents."""
    try:
        search_agent = yfinance_search_agent.create_agent()
        faiss_agent = sec_reports_retreival_agent.create_agent()
        orchestrator = orcherstrator_agent.create_orchestrator_agent(search_agent, faiss_agent)
        return orchestrator
    except Exception as e:
        st.error(f"Failed to initialize agents: {str(e)}")
        return None

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Financial Research Assistant",
        page_icon="💹",
        layout="wide"
    )

    # Custom CSS for improved styling
    st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
    }
    .stTextInput>div>div>input {
        height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title and description
    st.title("🔍 Financial Research Assistant")
    st.markdown("Get comprehensive financial insights with AI-powered research.")

    # Sidebar for additional controls
    st.sidebar.header("Research Options")
    research_depth = st.sidebar.slider(
        "Research Depth", 
        min_value=1, 
        max_value=5, 
        value=3, 
        help="Higher values may result in more detailed analysis"
    )

    # Initialize agents
    orchestrator = initialize_agents()
    
    if orchestrator is None:
        st.error("Could not initialize research agents. Please check your configuration.")
        return

    # Main input area
    query = st.text_input(
        "Enter your financial research query", 
        placeholder="e.g., Should I invest in Microsoft?",
        help="Ask about stocks, investment opportunities, or financial analysis"
    )

    # Research button
    if st.button("Research", type="primary"):
        if query:
            with st.spinner('Conducting financial research...'):
                try:
                    # Run the orchestrator agent
                    response = orchestrator.run(input=query)
                    
                    # Display results
                    st.subheader("Research Insights")
                    st.markdown(f'<div class="big-font">{response}</div>', unsafe_allow_html=True)
                    
                    # Optional: Add confidence/depth indicator based on slider
                    confidence_map = {
                        1: "Basic Overview",
                        3: "Comprehensive Analysis",
                        5: "Deep Dive Investigation"
                    }
                    st.info(f"Research Depth: {confidence_map.get(research_depth, 'Standard Analysis')}")
                
                except Exception as e:
                    st.error(f"An error occurred during research: {str(e)}")
        else:
            st.warning("Please enter a financial research query.")

    # Additional resources section
    st.sidebar.markdown("---")
    st.sidebar.header("💡 Quick Tips")
    st.sidebar.markdown("""
    - Be specific in your queries
    - Ask about stocks, companies, or investment strategies
    - Examples: "Analyze Apple's financial health", "Compare tech stocks"
    """)

if __name__ == "__main__":
    main()
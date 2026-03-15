import phoenix as px
session = px.launch_app()

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from graph import *

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

# 1. Setup the Tracer Provider
provider = TracerProvider()
# Replace with your actual OTLP endpoint (e.g., Jaeger, Honeycomb, or LangSmith)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# 2. Automatically instrument all LangChain calls
# This will catch your agent's tool calls and LLM steps
LangchainInstrumentor().instrument()

# Page configuration
st.set_page_config(
    page_title="🌍 AI Travel Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Initialize session state
if 'travel_agent' not in st.session_state:
    st.session_state.travel_agent = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


# def main():
#     # Header
#     st.markdown("""
#     <div style='text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 2rem;'>
#         <h1>🌍 AI Travel Agent & Expense Planner</h1>
#         <p>Plan your perfect trip with real-time data and detailed cost calculations</p>
#     </div>
#     """, unsafe_allow_html=True)
    
#     # API Status Check
#     st.sidebar.header("📡 API Status")
    
#     # Check API keys
#     # openai_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
#     serper_key = os.getenv("SERPER_API_KEY")
#     weather_key = os.getenv("OPENWEATHERMAP_API_KEY")
#     groq_key = os.getenv("GROQ_API_KEY")
    
#     # if openai_key:
#     #     st.sidebar.success("✅ OpenAI API")
#     # else:
#     #     st.sidebar.error("❌ OpenAI API Missing")
#     #     st.sidebar.info("Required for the app to work")
    
#     if serper_key:
#         st.sidebar.success("✅ Serper API")
#     else:
#         st.sidebar.warning("⚠️ Serper API Missing")
#         st.sidebar.info("Will use DuckDuckGo as fallback")
        
#     if weather_key:
#         st.sidebar.success("✅ Weather API")
#     else:
#         st.sidebar.warning("⚠️ Weather API Missing")
#         st.sidebar.info("Weather feature won't work")
    
#     # Main content
#     st.header("💬 Travel Query")
    
#     # Example queries
#     example_queries = {
#         "🏖️ Beach Vacation": """I want to visit Goa for 5 days in December.
# My budget is 30,000 INR.
# Get current weather for Goa.
# Find hotels under 3,000 INR per night.
# I want to know about beaches, water sports, and nightlife.
# Calculate exact costs including food (500 INR per day).
# Show me travel videos about Goa.""",
        
#         "🌍 International Trip": """I want to visit Thailand for 4 days.
# My budget is 800 USD.
# Convert all costs to Indian Rupees.
# Get current weather for Bangkok.
# Find budget hotels under 30 USD per night.
# Include street food and restaurant costs.
# Show temple entry fees and transportation costs.
# Calculate total trip cost in both USD and INR."""
#     }
    
#     selected_example = st.selectbox("🎯 Choose Example Query:", 
#                                    ["Custom Query"] + list(example_queries.keys()))
    
#     if selected_example != "Custom Query":
#         query = st.text_area("✍️ Your Travel Query:", 
#                             value=example_queries[selected_example],
#                             height=200)
#     else:
#         query = st.text_area("✍️ Your Travel Query:", 
#                             placeholder="E.g., I want to visit Paris for 7 days...",
#                             height=200)
    
#     # Process button
#     if st.button("🚀 Plan My Trip", type="primary", use_container_width=True):
#         if not query.strip():
#             st.warning("Please enter your travel query!")
#             return
        
#         # if not openai_key:
#         #     st.error("❌ OpenAI API key is required. Please add it to Streamlit secrets.")
#         #     return
        
#         # Initialize travel agent
#         if st.session_state.travel_agent is None:
#             with st.spinner("🔧 Initializing AI Travel Agent..."):
#                 st.session_state.travel_agent = initialize_travel_agent()
        
#         if st.session_state.travel_agent is None:
#             st.error("❌ Failed to initialize travel agent. Please check your API keys.")
#             return
        
#         # Process the query
#         with st.spinner("🤖 Planning your perfect trip..."):
#             try:
#                 response = st.session_state.travel_agent.invoke({
#                     "messages": [HumanMessage(query)]
#                 })
                
#                 # Display the response
#                 if response and "messages" in response:
#                     final_response = response["messages"][-1].content
#                     st.success("✅ Your travel plan is ready!")
#                     st.markdown(final_response)
                    
#                     # Add to chat history
#                     st.session_state.chat_history.append({
#                         "query": query,
#                         "response": final_response
#                     })
#                 else:
#                     st.error("❌ No response received. Please try again.")
                    
#             except Exception as e:
#                 st.error(f"❌ Error processing your request: {str(e)}")
#                 st.info("💡 Try refreshing the page or check your internet connection")

# if __name__ == "__main__":
#     main()



# Initialize session state variables
if "travel_agent" not in st.session_state:
    st.session_state.travel_agent = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def main():
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; 
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white; border-radius: 10px; margin-bottom: 2rem;'>
        <h1>🌍 AI Travel Agent & Expense Planner</h1>
        <p>Plan your perfect trip with real-time data and detailed cost calculations</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar: API status
    st.sidebar.header("📡 API Status")
    serper_key = os.getenv("SERPER_API_KEY")
    weather_key = os.getenv("OPENWEATHERMAP_API_KEY")
    
    st.sidebar.success("✅ Serper API" if serper_key else "⚠️ Serper API Missing")
    st.sidebar.success("✅ Weather API" if weather_key else "⚠️ Weather API Missing")
    
    # Chat section
    st.header("💬 Chat with Your Travel Agent")

    # Display chat history
    for chat in st.session_state.chat_history:
        st.markdown(f"**You:** {chat['query']}")
        st.markdown(f"**AI:** {chat['response']}")

    # Input for new query or follow-up
    query = st.text_area("✍️ Ask your travel question or follow-up:", height=100)

    if st.button("🚀 Send", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Please enter a question!")
            return

        # Initialize agent if not already
        if st.session_state.travel_agent is None:
            with st.spinner("🔧 Initializing AI Travel Agent..."):
                st.session_state.travel_agent = initialize_travel_agent()

        if st.session_state.travel_agent is None:
            st.error("❌ Failed to initialize travel agent. Check your API keys.")
            return

        # Append previous messages to maintain context
        messages = [HumanMessage(chat["query"]) for chat in st.session_state.chat_history]
        messages.append(HumanMessage(query))

        # Process the query
        with st.spinner("🤖 Thinking..."):
            try:
                response = st.session_state.travel_agent.invoke({"messages": messages})
                final_response = response["messages"][-1].content if response and "messages" in response else "Sorry, no response."

                # Update chat history
                st.session_state.chat_history.append({
                    "query": query,
                    "response": final_response
                })

                # Display the latest exchange immediately
                st.markdown(f"**You:** {query}")
                st.markdown(f"**AI:** {final_response}")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Check your connection or refresh the page")

if __name__ == "__main__":
    main()
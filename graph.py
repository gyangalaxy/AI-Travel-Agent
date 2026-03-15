from langgraph.graph import MessagesState, StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
# from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import streamlit as st
import os

from tools import *

def initialize_travel_agent():
    """Initialize the travel agent with all tools and configurations."""
    try:
        # Get OpenAI API key from Streamlit secrets or environment
        openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            st.error("❌ OpenAI API key not found. Please add it to Streamlit secrets.")
            st.info("💡 Go to Settings → Secrets and add: OPENAI_API_KEY = \"your-key-here\"")
            return None
        
        # Initialize OpenAI model - FIXED: Removed SecretStr
        # llm = ChatOpenAI(
        #     model="gpt-4o",
        #     temperature=0,
        #     max_tokens=2000,
        #     api_key=openai_api_key  # Direct string, not SecretStr
        # )

        llm = ChatGroq(
        # model_name="llama-3.3-70b-versatile",
        model_name="llama-3.1-8b-instant",
        temperature=0,           # 0 = deterministic — more reliable for structured output
        groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        # System prompt
        system_prompt = SystemMessage("""
        You are a professional AI Travel Agent. You MUST follow this EXACT process for every travel query:

        STEP 1: ALWAYS call get_weather tool first for the destination city

        STEP 2: ALWAYS call search_google or search_duck to find:
           - Hotels with specific prices per night
           - Top attractions with entry fees
           - Restaurants with price ranges
           - Transportation options with costs
           - CURRENCY CONVERSION: If user needs different currency, search for:
             "current exchange rate [from_currency] to [to_currency] today"

        STEP 3: ALWAYS use arithmetic tools (addition, multiply) to calculate:
           - Hotel cost = daily_rate × number_of_days
           - Total food cost = daily_food_budget × number_of_days
           - Total attraction costs = sum of all entry fees
           - Currency conversion = amount × exchange_rate (from search)
           - Grand total = hotel + food + attractions + transport

        STEP 4: ALWAYS call youtube_search for relevant travel videos

        STEP 5: Create detailed day-by-day itinerary with REAL costs from your searches

        MANDATORY RULES:
        - For currency conversion: SEARCH for current exchange rates, don't guess
        - Use ACTUAL data from tool calls, never make up prices
        - Show detailed cost breakdown with calculations
        - Include weather information from the weather tool
        - Provide YouTube video links from your search

        FORMAT your response as:
        ## 🌤️ Weather Information
        ## 💱 Currency Conversion  
        ## 🏛️ Attractions & Activities
        ## 🏨 Hotels & Accommodation
        ## 📅 Daily Itinerary
        ## 💰 Cost Breakdown
        ## 🎥 YouTube Resources
        ## 📋 Summary
        """)
        
        # Create tools list
        tools = [addition, multiply, division, substraction, get_weather, 
                search_google, search_duck, repl_tool, youtube_search]
        
        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(tools)
        
        # Create graph function
        def function_1(state: MessagesState):
            user_question = state["messages"]
            input_question = [system_prompt] + user_question
            response = llm_with_tools.invoke(input_question)
            return {"messages": [response]}
        
        # Build the graph
        builder = StateGraph(MessagesState)
        builder.add_node("llm_decision_step", function_1)
        builder.add_node("tools", ToolNode(tools))
        builder.add_edge(START, "llm_decision_step")
        builder.add_conditional_edges("llm_decision_step", tools_condition)
        builder.add_edge("tools", "llm_decision_step")
        
        # Compile the graph
        react_graph = builder.compile()
        return react_graph
        
    except Exception as e:
        st.error(f"❌ Error initializing travel agent: {str(e)}")
        st.info("💡 Check your API keys and internet connection")
        return None

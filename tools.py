from langchain.tools import tool
from langchain_community.utilities import OpenWeatherMapAPIWrapper, GoogleSerperAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun, YouTubeSearchTool
from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL
import streamlit as st
import os

# Custom Tools
@tool
def addition(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

@tool
def division(a: int, b: int) -> float:
    """Divide two integers."""
    if b == 0:
        raise ValueError("Denominator cannot be zero.")
    return a / b

@tool
def substraction(a: int, b: int) -> float:
    """Subtract two integers."""
    return a - b

@tool
def get_weather(city: str) -> str:
    """Fetches the current weather of the city from OpenWeatherMap."""
    try:
        weather_api_key = st.secrets.get("OPENWEATHERMAP_API_KEY") or os.getenv("OPENWEATHERMAP_API_KEY")
        if weather_api_key:
            os.environ["OPENWEATHERMAP_API_KEY"] = weather_api_key
            weather = OpenWeatherMapAPIWrapper()
            return weather.run(city)
        else:
            return f"Weather API key not available. Cannot get weather for {city}."
    except Exception as e:
        return f"Weather data unavailable for {city}. Error: {str(e)}"

@tool
def search_google(query: str) -> str:
    """Fetches details about attractions, restaurants, hotels, etc. from Google Serper API."""
    try:
        serper_api_key = st.secrets.get("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")
        if serper_api_key:
            os.environ["SERPER_API_KEY"] = serper_api_key
            search_serper = GoogleSerperAPIWrapper()
            return search_serper.run(query)
        else:
            # Fallback to duck search if serper not available
            return search_duck(query)
    except Exception as e:
        return f"Google search unavailable, trying alternative search. Error: {str(e)}"

@tool
def search_duck(query: str) -> str:
    """Fetches details using DuckDuckGo search."""
    try:
        search_d = DuckDuckGoSearchRun()
        return search_d.invoke(query)
    except Exception as e:
        return f"Search unavailable. Error: {str(e)}"

@tool
def youtube_search(query: str) -> str:
    """Fetches YouTube videos about travel destinations."""
    try:
        youtubetool = YouTubeSearchTool()
        return youtubetool.run(query)
    except Exception as e:
        return f"YouTube search unavailable. Error: {str(e)}"

# Advanced calculation tool
python_repl = PythonREPL()
repl_tool = Tool(
    name="python_repl",
    description="A Python shell for complex calculations. Input should be a valid python command.",
    func=python_repl.run,
)

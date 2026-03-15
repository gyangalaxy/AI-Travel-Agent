# AI Travel Agent (Streamlit + LangGraph)

Streamlit front-end backed by a LangGraph-powered travel agent that calls external tools (search, weather, YouTube) and performs cost math to return a day-by-day itinerary with real prices.

## Architecture
- **UI:** `streamlit_app.py` renders the chat-style interface and manages session state/history.
- **Agent runtime:** `graph.py` builds a LangGraph with a single LLM node (`ChatGroq` llama-3.1-8b-instant) and a `ToolNode`. The LLM emits structured tool calls; the graph loops LLM → tools → LLM until completion.
- **Tools:** Implemented in `tools.py` using LangChain tool decorators:
  - Search: `search_google` (Serper) with DuckDuckGo fallback.
  - Weather: `get_weather` (OpenWeatherMap).
  - Media: `youtube_search`.
  - Math helpers: `addition`, `multiply`, `division`, `substraction`, plus a general-purpose `python_repl`.
- **Observability:** OpenTelemetry traces are exported to an OTLP endpoint at `http://localhost:4317` and Phoenix is launched locally via `phoenix.launch_app()`. LangChain auto-instrumentation captures tool and LLM spans.
- **Configuration:** Environment variables are loaded with `dotenv`; Streamlit theme/server options live in `streamlit_config.txt` (copy into `.streamlit/config.toml` if desired). A sample `.env` is auto-created by `run_script.py` if missing.

## Data flow (request → response)
1) User submits a travel query in Streamlit.
2) `initialize_travel_agent()` constructs the graph, binds tools, and seeds the system prompt (enforces weather lookup, price searches, currency conversion, math, and YouTube links).
3) The graph starts at the LLM node; when tool calls are returned they are executed by `ToolNode` and fed back to the LLM until it produces the final message.
4) Streamlit displays the assistant reply and appends the exchange to `chat_history`.

## Project layout
- `streamlit_app.py` – main app entry point (`streamlit run streamlit_app.py`).
- `graph.py` – LangGraph construction and system prompt.
- `tools.py` – tool definitions (search, weather, YouTube, math, Python REPL).
- `requirements.txt` – Python dependencies.
- `run_script.py` – convenience installer/launcher (expects `streamlit_app.py`; update if renamed).
- `.streamlit/secrets.toml` – Streamlit secrets (contains API keys; do not commit).
- `streamlit_config.txt` – theme/server defaults (optional copy to `.streamlit/config.toml`).
- `gitignore_file.txt` – rename to `.gitignore` before publishing the repo.

## Setup
1) Python 3.10+ recommended.
2) Create venv: `python -m venv .venv && .\.venv\Scripts\activate`
3) Install deps: `pip install -r requirements.txt`
4) Configure environment (choose one):
   - `.env` file in repo root with:
     ```
     OPENAI_API_KEY=...
     GROQ_API_KEY=...  (optional)
     SERPER_API_KEY=...
     OPENWEATHERMAP_API_KEY=...
     ```
   - or `.streamlit/secrets.toml` with the same keys.
5) Start app: `streamlit run streamlit_app.py`
6) (Optional) Start an OTLP collector (Jaeger/Tempo/etc.) listening on `http://localhost:4317` to receive traces; Phoenix UI auto-launches via `phoenix.launch_app()`.

## Operational notes
- The agent currently uses Groq by default; OpenAI support is scaffolded but commented out in `graph.py`.
- `run_script.py` still references `app.py`; change to `streamlit_app.py` if you use the helper script.
- Clear any real API keys from `.streamlit/secrets.toml` before committing. Keep `.env`, `.streamlit/secrets.toml`, and `.ignore/` out of version control via `.gitignore`.
- Currency conversion is expected to come from live search results; the system prompt instructs the model not to guess rates.

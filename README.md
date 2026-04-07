# TravelBuddy: LangGraph Visual Execution Engine

TravelBuddy is an intelligent, agent-based travel assistant powered by the [LangGraph](https://python.langchain.com/v0.1/docs/langgraph/) ReAct architecture. In addition to answering travel-related queries, this project features a **real-time, transparent playback UI** that allows developers to visualize the agent's internal reasoning, step-by-step state transitions, and tool-invocation sequences.

## 🌟 Key Features

* **LangGraph ReAct Core**: A robust cyclic graph representing the agent's autonomous planning loop (`Start` → `Agent` → `Tools` ↺ → `End`).
* **Live Graph Visualization**: An interactive, dynamic node network built with `vis.js`. Nodes and edges glow and animate synchronously with the backend LLM execution stream.
* **Reasoning Timeline Player**: A time-traveling developer log on the UI. The execution buffers via WebSockets, allowing the user to precisely Pause, Play, Step Next, or Step Back through the LLM's thought process.
* **Context Streaming**: A modern `FastAPI` instance managing WebSocket connections, streaming LangGraph states rapidly to the frontend without blocking.

## 🏗️ Architecture

1. **Agent (`agent.py`) & Tools (`tools.py`)**: 
   Defines a conditional graph workflow. Depending on the query, the `Agent` node analyzes intent and routes either to the `Tools` node (for functions like `search_flights`, `search_hotels`, `calculate_budget`) or the `End` node.
2. **Backend Engine (`server.py`)**: 
   A lightweight `FastAPI` server. It captures LangGraph execution via `graph.stream()`, broadcasts `node_executed` updates, and extracts detailed LLM reasoning (tool mapping, raw inferences) asynchronously.
3. **Frontend Dashboard (`index.html`)**: 
   A stunning, dependency-free (via CDNs) single-page HTML interface combining Tailwind CSS, custom playback logic, and `vis-network`. 

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.9+ installed. Follow these steps to set up the environment:

```bash
# Install the required server and agent libraries
pip install fastapi uvicorn websockets langgraph langchain-openai python-dotenv
```

### Environment Variables
You will need your LLM provider API credentials. Ensure your `.env` file is properly configured. If you are using GitHub models context as written in `agent.py`:
```bash
GITHUB_TOKEN=your_github_personal_access_token_here
```

### Running the Application

1. **Start the FastAPI Server:**
   Navigate to the project directory and run:
   ```bash
   python3 server.py
   ```
2. **Open the Dashboard:**
   Visit [http://localhost:8000](http://localhost:8000) in your web browser.

## 🎮 How to Use the UI 

1. **Query the Chatbot:** Type a request requiring tools in the left panel (e.g., *"Find flights from Da Nang to Ha Noi"*).
2. **Watch the Execution:** Observe the center graph. The system will automatically execute and animate the workflow path on the graph. 
3. **Engine Logs & Playback:** 
   * Hit **Pause** to halt the visual rendering.
   * Use the **Next/Prev** buttons (or your keyboard's **Left/Right Arrow keys**) to manually step through the timeline.
   * Inspect the right-hand **Engine Logs** pane to read carefully formatted summaries of the exact tool definitions dispatched and processed.

## 🤝 Project Structure
```text
.
├── agent.py               # Core LangGraph execution definitions
├── tools.py               # Functional external tool integrations
├── server.py              # FastAPI websocket streaming orchestrator
├── index.html             # Advanced 3-pane interactive frontend dashboard
├── .env                   # Environment variable injection
└── README.md              # Project documentation
```
## 🔬 Lab Results & Deliverables

All required files and deliverables for this assignment have been organized into the `/solution` directory

---
*Created for Lab 4 – LangGraph Agent Assignment*

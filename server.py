import os
import json
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# Import your graph and state
from agent import graph

app = FastAPI()

@app.get("/")
async def get():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state = {"messages": []}
    
    try:
        while True:
            data = await websocket.receive_text()
            user_msg = json.loads(data).get("message", "")
            if not user_msg:
                continue
                
            state["messages"].append(("human", user_msg))
            
            # Send initial event
            await websocket.send_json({
                "type": "node_executed", 
                "node": "__start__",
                "details": "User input received.\nInitializing ReAct loop..."
            })
            
            # The backend loops as fast as it can. The frontend buffers and controls playback!
            for output in graph.stream(state):
                for node_name, node_update in output.items():
                    # Extract the reasoning logs!
                    new_msgs = node_update.get("messages", [])
                    if not isinstance(new_msgs, list):
                        new_msgs = [new_msgs]
                        
                    reasoning_text = []
                    for m in new_msgs:
                        if m.type == "ai":
                            if hasattr(m, 'tool_calls') and m.tool_calls:
                                calls = [f"⚡ {tc['name']}({tc['args']})" for tc in m.tool_calls]
                                reasoning_text.append(f"Decided to map tools:\n" + "\n".join(calls))
                            elif m.content:
                                reasoning_text.append("Synthesizing final response based on tool context.")
                        elif m.type == "tool":
                            # Truncate long tool outputs
                            content = str(m.content)
                            preview = content[:200] + "..." if len(content) > 200 else content
                            reasoning_text.append(f"✓ Tool '{m.name}' returned:\n{preview}")
                            
                    details = "\n\n".join(reasoning_text) if reasoning_text else "Processed state successfully."
                    
                    # Store updated context
                    state["messages"].extend(new_msgs)

                    # Stream buffer
                    await websocket.send_json({
                        "type": "node_executed", 
                        "node": node_name,
                        "details": details
                    })
                    await asyncio.sleep(0.05) # Tiny micro-gap to prevent websocket flooding

            final_message = state["messages"][-1].content
            await websocket.send_json({
                "type": "final_answer", 
                "text": final_message,
                "node": "__end__",
                "details": "Graph execution completed.\nAnswer presented to user."
            })
            
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    print("Starting LangGraph UI server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

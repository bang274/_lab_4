import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from .tools import search_flights, search_hotels, calculate_budget
from dotenv import load_dotenv

load_dotenv()

# Get the directory of this file
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Đọc System Prompt
with open(os.path.join(APP_DIR, "system_prompt.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM và Tools
tools_list = [search_flights, search_hotels, calculate_budget]

# Configured to use GitHub PAT as per previous request
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ.get("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent Node
def agent_node(state: AgentState):
    messages = state["messages"]
    # Thêm System Prompt vào đầu nếu chưa có
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm_with_tools.invoke(messages)
    
    # === LOGGING ===
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"Gọi tool: {tc['name']}({tc['args']})")
    else:
        print(f"Trả lời trực tiếp")
        
    return {"messages": [response]}

# 5. Xây dựng Graph
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)

tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

# Khai báo edges để tạo vòng lặp ReAct
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile()
def save_graph_image(graph, filename="agent_graph.png"):
    try:
        # Requires extra dependencies installed
        graph.get_graph().draw_mermaid_png(output_file_path=filename)
        print(f"Graph saved to {filename}")
    except Exception as e:
        print(f"Error saving PNG: {e}")
        # Fallback to printing the mermaid string
        print("Mermaid string for copy-paste:")
        print(graph.get_graph().draw_mermaid())

save_graph_image(graph)

# 6. Chat loop
# if __name__ == "__main__":
#     print("=" * 60)
#     print("TravelBuddy – Trợ lý Du lịch Thông minh")
#     print("Gõ 'quit' để thoát")
#     print("=" * 60)
    
#     # Initialize state with empty messages list
#     state = {"messages": []}
    
#     while True:
#         user_input = input("\nBạn: ").strip()
#         if user_input.lower() in ("quit", "exit", "q"):
#             break
            
#         print("\nTravelBuddy đang suy nghĩ...")
#         # Invoke graph với lịch sử tin nhắn
#         # graph.invoke returns the updated state
#         state["messages"].append(("human", user_input))
#         state = graph.invoke(state)
        
#         # Lấy message cuối cùng (phản hồi của agent)
#         final = state["messages"][-1]
#         print(f"\nTravelBuddy: {final.content}")

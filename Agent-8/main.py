from typing import TypedDict, Literal, Sequence, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.tools import tool
import os
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
@tool
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers together"""
    return a - b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b

tools = [add, subtract, multiply]

llm_with_tools = llm.bind_tools(tools)


def llm_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="You are an AI assistant, Please answer my query to the best of your ability.")
    response = llm_with_tools.invoke([system_prompt] + state["messages"])
    print("#" * 150)
    print("response: ", response)
    print("#" * 150)
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["end", "continue"]:
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "end"
    else: 
        return "continue"
    
graph = StateGraph(AgentState)
graph.add_node("call_llm_node", llm_call)

tool_node = ToolNode(tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("call_llm_node")
graph.add_conditional_edges(
        "call_llm_node", 
        should_continue,
        {
            "end": END,
            "continue": "tools"
        }
    )

graph.add_edge("tools", "call_llm_node")

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s['messages'][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()
    

inputs = {"messages": ["22 + 12 and 10 * 5 also 100 - 2"]}
print_stream(app.stream(inputs, stream_mode="values"))
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.types import interrupt
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

@tool
def human_assistance(query: str):
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    print("#" *150)
    print("Human responses: ", human_response)
    print("#" *150)

    return human_response["data"]

tools = [human_assistance]

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

# llm = init_chat_model(model_provider="google_genai", model='gemini-2.0-flash')
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
   
)

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State): 
    # messages = state.get("messages")
    # response = llm_with_tools.invoke(messages)
    # return {"messages": [response]}
    message = llm_with_tools.invoke(state["messages"])
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}
    

graph_builder = StateGraph(State)

# built-in Node
tool_node = ToolNode(tools=tools)

# Nodes 
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("chatbot", chatbot)

# Edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)


# this is without MEMORY. 
graph = graph_builder.compile()


# this is with MEMORY
def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

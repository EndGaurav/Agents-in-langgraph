from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    message: str
    
def greeting_node(state: AgentState) -> AgentState:
    """Simple node that adds a greeting message to the state"""
    state["message"] = f"{state['message']}, you are doing an amazing job learning langgraph!"
    return state

graph = StateGraph(AgentState)

graph.add_node("greeting_nodee", greeting_node)

graph.add_edge(START, "greeting_nodee")
graph.add_edge("greeting_nodee", END)


app = graph.compile()



result = app.invoke({"message": "Bob"})

print(result["message"])


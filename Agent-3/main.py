from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    name: str
    age: str
    final: str
    
def first_node(state: AgentState) -> AgentState:
    """This is the first node of our sequeence"""
    state["final"] = f"HII {state['name']}"
    return state

def second_node(state: AgentState) -> AgentState:
    """This is the second node of our sequeence"""
    state["final"] = f"{state['final']}, You are {state['age']} years old"
    return state

graph = StateGraph(AgentState)

graph.add_node("f_node", first_node)
graph.add_node("s_node", second_node)

graph.add_edge(START, "f_node")
graph.add_edge("f_node", "s_node")
graph.add_edge("s_node", END)


app = graph.compile()



result = app.invoke({"name": "Bob", "age": "12"})

print(result["final"])


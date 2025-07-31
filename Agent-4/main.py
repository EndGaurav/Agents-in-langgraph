from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    number1: int
    number2: int
    
    operator: str
    final: int
    
    
def add(state: AgentState) -> AgentState:
    """Add two numbers together."""
    state["final"] = state["number1"] + state["number2"]
    return state

def subtract(state: AgentState) -> AgentState:
    """Subtract two numbers together."""
    state["final"] = state["number1"] - state["number2"]
    return state

def decide(state: AgentState) -> Literal["addition_operation", "subtract_operation"]:
    """Based on operator decide which node to execute."""
    if state["operator"] == "+":
        return "addition_operation"
    elif state["operator"] == "-":
        return "subtract_operation"


graph = StateGraph(AgentState)

graph.add_node("add_node", add)
graph.add_node("subtract_node", subtract)
graph.add_node("router", lambda state:state)

graph.add_edge(START, "router")
graph.add_conditional_edges(
        "router", 
        decide, 
        {
            # edge: node (format of path map) this 3rd argument called the path map for the router.
            "addition_operation": "add_node",
            "subtract_operation": "subtract_node"
        }
    )


graph.add_edge("add_node", END)
graph.add_edge("subtract_node", END)


app = graph.compile()

result = app.invoke({"number1": 100, "number2": 200, "operator": "+"})

print(result)
print(result["final"])


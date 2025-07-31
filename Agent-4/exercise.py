from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class AgentState(TypedDict):
    number1: int
    number2: int
    number3: int
    number4: int
    final1: int
    final2: int
    operator1: str
    operator2: str
    
def add(state: AgentState) -> AgentState:
    """Simple function which add two numbers"""
    state["final1"] = state["number1"] + state["number2"]
    return state

def minus(state: AgentState) -> AgentState:
    """Simple function which minus two numbers"""
    
    state['final1'] = state['number1'] - state['number2']
    return state

def add2(state: AgentState) -> AgentState:
    """Simple function which add two numbers"""
    state["final2"] = state["number3"] + state["number4"]
    return state

def minus2(state: AgentState) -> AgentState:
    """Simple function which minus two numbers"""
    state['final2'] = state['number3'] - state['number4']
    return state

def first_router(state: AgentState) -> Literal["addition_operation_1", "minus_operation_1"]:
    """First router function"""
    if state["operator1"] == "+":
        return "addition_operation_1"
    elif state["operator1"] == "-":
        return "minus_operation_1"
 
def second_router(state: AgentState) -> Literal["addition_operation_2", "minus_operation_2"]:
    """Second router function"""
    if state["operator2"] == "+":
        return "addition_operation_2"
    elif state["operator2"] == "-":
        return "minus_operation_2"
    

graph = StateGraph(AgentState)

graph.add_node("add_node_1", add)
graph.add_node("minus_node_1", minus)
graph.add_node("minus_node_2", minus2)
graph.add_node("add_node_2", add2)
graph.add_node("router_1", lambda state: state)
graph.add_node("router_2", lambda state: state)

graph.add_edge(START, "router_1")
graph.add_conditional_edges("router_1", first_router, {"addition_operation_1": "add_node_1", "minus_operation_1": "minus_node_1"})
graph.add_edge("add_node_1", "router_2")
graph.add_edge("minus_node_1", "router_2")
graph.add_conditional_edges("router_2", second_router, {"addition_operation_2": "add_node_2", "minus_operation_2": "minus_node_2"})

graph.add_edge("add_node_2", END)
graph.add_edge("minus_node_2", END)

app = graph.compile()

result = app.invoke({"number1": 20, "number2": 5, "operator1": "+", "number3": 10, "number4": 5, "operator2": "-"})
print(result)
print(result['final1'])
print(result['final2'])

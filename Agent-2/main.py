from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    values: list[int]
    name: str
    result: str
    operation: str
    
    
def multiple(values: list[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result     

def add(values: list[int]) -> int:
    result = 0
    for value in values:
        result += value
    return result     
    
def process_values(state: AgentState) -> AgentState:
    """This function handles multiple different inputs"""
    
    if state["operation"] == "*":
        state["result"] = f"Hii {state['name']}, your result is {multiple(state['values'])}"
    elif state["operation"] == "+":
        state["result"] = f"Hii {state['name']}, your result is {add(state['values'])}"
    
    return state

graph = StateGraph(AgentState)

graph.add_node("process_values", process_values)

graph.add_edge(START, "process_values")
graph.add_edge("process_values", END)

app = graph.compile()

result = app.invoke({"values": [1,2,3,4,5], "name":"alex", "operation": "+"})

print(result["result"])
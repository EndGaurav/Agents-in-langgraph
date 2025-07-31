from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class AgentState(TypedDict):
    name: str
    age: int
    skills: list[str]
    result: str
    

def greeting(state: AgentState) -> AgentState:
    """A simple function which greets the user"""
    state['name'] = state['name'] + ", welcome to the system"
    
    return state

def describe_user_age(state: AgentState) -> AgentState:
    """A simple function which tells user's age"""
    state['age'] = f"You are {state['age']} years old!"
    
    return state

def express_user_skills(state: AgentState) -> AgentState:
    """A simple function which tells user's skills"""
    state['result'] = state['name'] + " " + state['age'] + " " + "You have skills in: " + ", ".join(state['skills'])
    
    return state


graph = StateGraph(AgentState)

graph.add_node("first_node", greeting)
graph.add_node("second_node", describe_user_age)
graph.add_node("third_node", express_user_skills)

graph.add_edge(START, "first_node")
graph.add_edge("first_node", "second_node")
graph.add_edge("second_node", "third_node")
graph.add_edge("third_node", END)

app = graph.compile()

result = app.invoke({"name": "John", "age": 25, "skills": ["Python", "Java", "C++"]})

print(result['result'])
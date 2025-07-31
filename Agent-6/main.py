from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

class AgentState(TypedDict):
    messages: List[HumanMessage]
    
def process(state: AgentState) -> AgentState:
    result = llm.invoke(state['messages'])
    print(f"\nAI: {result.content}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process_node", process)
graph.add_edge(START, "process_node")
graph.add_edge("process_node", END)

app = graph.compile()

while True:
    user_query = input("> ")
    if user_query == "exit":
        break
    app.invoke({"messages": [HumanMessage(user_query)]})


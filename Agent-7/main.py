from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv() 

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]
   
   
def process(state: AgentState) -> AgentState:
    """This node will resolve you query given in input."""
    response = llm.invoke(state['messages'])
    
    state['messages'].append(AIMessage(content=response.content))
    print(f"\nAI: {response.content}")
    return state

graph = StateGraph(AgentState)

graph.add_node("process_node", process)
graph.add_edge(START, "process_node")
graph.add_edge("process_node", END)


app = graph.compile()

conversation_history = []
while True:
    user_query = input("> ")
    conversation_history.append(HumanMessage(user_query))
    if user_query == "quit":
        break
    result = app.invoke({"messages": conversation_history})
    print(result['messages'])
    
with open("conversation.txt", "w") as file:
    file.write("Your conversation history:\n")
    for message in conversation_history:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n\n")
    file.write("End of Conversation")
    
print("Conversation history saved to conversation.txt")
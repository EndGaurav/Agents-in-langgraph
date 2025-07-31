from typing import TypedDict, Literal, Sequence, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.tools import tool
import os
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

document_content = ""

@tool
def update(content: str) -> str:
    """Updates the document with the provided content."""
    global document_content
    document_content = content
    return f"Document has been updated successfully! The current content is: \n{document_content}"

@tool
def save(filename: str) -> str:
    """Save the current document to a text file and finish the process
    Args:
        filename: Name of the text file
    """
    
    global document_content
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"
        
    try:
        with open(filename, "w") as file:
            file.write(document_content)
        print(f"\nDocument has been save to: {filename}")
        return f"Document has been saved successfully to {filename}."
    except Exception as e:
        return f"Error saving document: {str(e)}"
    
tools = [update, save]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
llm_with_tools = llm.bind_tools(tools)

def our_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.
    
    - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
    - If the user wants to save and finish, you need to use the 'save' tool.
    - Make sure to always show the current document state after modifications.
    
    The current document content is:{document_content}                             
    """)

    if not state['messages']:
        user_input = "I'm ready to help you update a document. What would you like to create?"
        user_message = HumanMessage(content=user_input)
        
    else: 
        user_input = input("\nWhat would you like to do with the document? ")
        print(f"\n👤 USER: {user_input}")
        user_message = HumanMessage(content=user_input)
    
    all_messages = [system_prompt] + list(state['messages']) + [user_message]
    
    response = llm_with_tools.invoke(all_messages) 
    print("*"*100)
    print(response)   
    print("*"*100)   

    print(f"\n🤖 AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"🔍 USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")
        
    return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end the conversation."""
    messages = state['messages']
    if not messages:
        return "continue"
    
    for message in reversed(messages):
        if (isinstance(message, ToolMessage)) and "saved" in message.content.lower() and "document" in message.content.lower():
            return "end"
        
    return "continue"
            
            
            
graph = StateGraph(AgentState)

tool_node = ToolNode(tools)

graph.add_node("agent_node", our_agent)
graph.add_node("tool_node", tool_node)


graph.set_entry_point("agent_node")
graph.add_edge("agent_node", "tool_node")
graph.add_conditional_edges(
    "tool_node",
    should_continue,
    {
        "end": END,
        "continue": "agent_node"
    }
)
graph.add_edge("tool_node", "agent_node")

app = graph.compile()

def print_messages(messages):
    """Function I made to print the messages in a more readable format."""
    if not messages:
        return
    
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"🔨 TOOl RESULT: {message.content}")

def run_document_agent():
    print("\n ===== DRAFTER =====")
    
    state = {"messages": []}
    
    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step['messages'])
            
    print("\n ===== DRAFTER =====")
    
if __name__ == "__main__":
    run_document_agent()
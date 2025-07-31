from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Literal
from dotenv import load_dotenv
from langsmith.wrappers import wrap_openai
from openai import OpenAI
import os
from pydantic import BaseModel

load_dotenv()


client = wrap_openai(OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
))

class Detect_Call_Response(BaseModel):
    is_ai_question: bool
    
class CodingAIResponse(BaseModel):
    answer: str

class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool
    
def detect_query(state: State):
    user_message = state.get("user_message")
    
    SYSTEM_PROMPT = """
        You are an AI assistant. Your job is to tell weather a user query is related to coding question or not. 
        Return the response in boolean only.
    """
    
    # Open AI call
    response = client.beta.chat.completions.parse(
            model="gemini-2.0-flash",
            response_format=Detect_Call_Response,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT },
                {"role": "user", "content": user_message}
            ]
        )
    
    # print("response from model: ", response.choices[0].message.parsed.is_ai_question)
    state["is_coding_question"]  = response.choices[0].message.parsed.is_ai_question
    return state

def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"] :
    is_coding_question = state.get("is_coding_question")
    
    if is_coding_question: 
        
        return "solve_coding_question"
    else:
        
        return "solve_simple_question"

def solve_coding_question(state: State):
    user_query = state.get("user_message")
    
    # Open AI call for solving the question (Advance model)
    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to resolve the user query based on coding 
    problem he is facing
    and also provide example as well which user can easily understand.
    """
    response = client.beta.chat.completions.parse(
            model="gemini-2.0-flash",
            response_format=CodingAIResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ]
        )
    
    print("Response from coding model: ", response.choices[0].message.parsed.answer)
    state["ai_message"] = response.choices[0].message.parsed.answer
    
    return state

def solve_simple_question(state: State):
    user_query = state.get("user_message")
    
    # Open AI call (Basic model)
    SYSTEM_PROMPT = """
    You are an AI assistant. Your ONLY job is to chat with the user.
    """
    
    response = client.beta.chat.completions.parse(
            model="gemini-2.0-flash",
            response_format=CodingAIResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ]
        )
    
    print("Response from normal model: ", response.choices[0].message.parsed.answer)
    state["ai_message"] = response.choices[0].message.parsed.answer
    
    return state 

graph_builder = StateGraph(State)

graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question) 
graph_builder.add_node("route_edge", route_edge) 

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_edge)

graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()

# Use the graph

def call_graph():
    user_query = input("> ")
    state = {
        "user_message": user_query,
        "ai_message": "",
        "is_coding_question": False
    }
    result = graph.invoke(state)
    # print("Final response: ", result["user_message"])
    
    return result["user_message"]

while True:
        
    user_query = call_graph()
    
    if user_query in ["bye"]: 
        break
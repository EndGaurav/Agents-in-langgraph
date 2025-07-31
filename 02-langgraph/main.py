from langgraph_chat_with_interrupt import create_chat_graph
from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver
import os 

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_URI = MONGODB_URI
config = {"configurable": {"thread_id": "6"}}

def init():
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph_with_mongodb = create_chat_graph(checkpointer=checkpointer)
        while True:
            user_query = input("> ")
            
            for event in graph_with_mongodb.stream({ "messages": [{"role": "user", "content": user_query}] }, stream_mode="values", config=config):
                if "messages" in event:
                    # print(event["messages"])
                    event["messages"][-1].pretty_print()
        
        
init()
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver 
from contextlib import contextmanager

model = init_chat_model(
    "gemma3:latest",
    model_provider="ollama",
    base_url="http://localhost:11434" # Note the http:// prefix required here
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

#node defination
def chatbot(state: State):
    response = model.invoke(state.get("messages"))
    #print("\n\nInside chatbot node", response)
    return {"messages": [response]}

#adding nodes to graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

#adding edges to graph
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

#contexmanager used to handle stateless else graph will be null while returning
@contextmanager
def compile_graph_with_checkpointer():
    DB_URI = "mongodb://admin:admin@localhost:27017"
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph = graph_builder.compile(checkpointer=checkpointer)
        yield graph

config = {
        "configurable": {
            "thread_id": "Bibhukalyan"
        }
    }

with compile_graph_with_checkpointer() as graph_with_checkpointer:
    #Checkpointer is used to save the state of the graph
    #graph = graph_builder.compile()
    #use above 1 for not using checkpoint
    #updated_state = graph_with_checkpointer.invoke(State({"messages": ["what is my name?"]}), config=config)
    #for streaming and getting last message
    user_query = input("👉 what are you looking for? ")
    for chunk in graph_with_checkpointer.stream(State({"messages": [user_query]}), config=config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

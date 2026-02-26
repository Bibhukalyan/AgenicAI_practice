from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model


llm = init_chat_model(
    "gemma3:latest",
    model_provider="ollama",
    base_url="http://localhost:11434" # Note the http:// prefix required here
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

#node defination
def chatbot(state: State):
    response = llm.invoke(state.get("messages"))
    print("\n\nInside chatbot node", response)
    return {"messages": [response]}

#node defination
def samplenode(state: State):
    print("\n\nInside samplenode", state, "\n\n")
    return {"messages": ["i am a sample node"]}

#adding nodes to graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", samplenode)

#adding edges to graph
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "samplenode")
graph_builder.add_edge("samplenode", END)

graph = graph_builder.compile()
updated_state = graph.invoke(State({"messages": ["Hi, i am bibhukalyan"]}))
print("Updated state after graph execution:", updated_state)

from fastapi import FastAPI, Body
from ollama import Client
import requests

app = FastAPI()
client = Client(
   host="localhost:11434",
)

def get_weather(city: str) -> str:
    """
    Get the current weather for a specific city.
    Args:
        city: The name of the city to check.
    """

    url = f"https://wttr.in/{city.lower()}?format=%C+%t"

    response = requests.get(url)
    if response.status_code == 200:
        print(f"Weather data for {city}: {response.text}") 
    else:
        print(f"Failed to get weather data for {city}. Status code: {response.status_code}")

available_functions = {
    "get_weather": get_weather,
}


get_weather("Delhi")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/message")
def read_root():
    return {"Hello": "Bibhukalyan"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.post("/chat")
def chat(message: str = Body(..., description="The message")):
    messages = [{"role": "user", "content": message}]
    # response = client.chat(model="gemma3:latest",messages=messages
    # )

    #return {"response": response.message.content}

    response = client.chat(
        model="gemma3:latest",messages=[
        {"role": "user", "content": message}],
        tools=[get_weather],
    )
    

    if response.message.tool_calls:
        # Add the model's request to the conversation history
        messages.append(response.message)

        # Process each tool call suggested by the model
        for tool in response.message.tool_calls:
            function_to_call = available_functions.get(tool.function.name)
            if function_to_call:
                # Execute the real Python function
                print(f"Agent is calling: {tool.function.name}({tool.function.arguments})")
                tool_result = function_to_call(**tool.function.arguments)

                # Add the tool result back to the message list
                messages.append({
                    "role": "tool",
                    "content": tool_result,
                })

        # Step C: Send the updated history (with tool output) back to the LLM
        final_response = client.chat(model="gemma3:latest", messages=messages)
        return {"response": final_response.message.content}

    # If no tool was needed, just return the plain response
    return {"response": response.message.content}



# for part in client.chat('gpt-oss:120b-cloud', messages=messages, stream=True):
#   print(part.message.content, end='', flush=True)
import os
import json
import requests
import certifi
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
# 1) Client for Gemini via OpenAI-compatible endpoint
openai_gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_KEY_1"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# tool to run system commands// not added yet to tool router, just for demo
def run_command(command: str) -> str:
    try:
        result = os.popen(command).read().strip()
        return f"Command output: {result}"
    except Exception as e:
        return f"Error running command '{command}': {e}"

# 2) Tool implementation (return string instead of print, so the model can use it)
def get_weather(city: str) -> str:
    if not city or not isinstance(city, str):
        return "Invalid city name."
    url = f"http://wttr.in/{city.lower()}?format=%C+%t"
    try:
        response = requests.get(url, timeout=10, verify=certifi.where())
        if response.status_code == 200:
            return f"Weather in {city} is {response.text.strip()}"
        else:
            return f"Could not retrieve weather data for {city}. HTTP {response.status_code}"
    except requests.RequestException as e:
        return f"Error retrieving weather for {city}: {e}"

# 3) Tool schema (must match the function name exactly)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get a quick current weather summary for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g., 'Delhi' or 'Bengaluru'.",
                    }
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a windows command and return the output or error.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The windows command to run, e.g., 'dir' or 'echo hello'.",
                    }
                },
                "required": ["command"],
                "additionalProperties": False,
            },
        },
    }
]

# Optional: map tool names to local callables if you add more tools later
TOOL_ROUTER = {
    "get_weather": get_weather,
    "run_command": run_command
}

#class MyOutputFormat(BaseModel):


# 4) Small agent loop: lets the model decide to call tools, executes, and returns final answer
# def run_agent(user_message: str) -> str:
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are a helpful assistant. If the user asks about current weather, "
#                 "use the get_weather tool. After using a tool, summarize the result clearly."
#             ),
#         },
#         {"role": "user", "content": user_message},
#     ]

#     # First turn: allow tool calls
#     resp = openai_gemini_client.chat.completions.create(
#         model="gemini-2.5-flash",
#         messages=messages,
#         tools=tools,
#         tool_choice="auto",
#         temperature=0.2,
#         #output_format={"type": "json_object", "class": MyOutputFormat.model_json_schema()},
#     )
#     print("RAW MODEL RESPONSE:", resp)
#     msg = resp.choices[0].message
#     messages.append(msg)

#     while msg.tool_calls:
#         for tc in msg.tool_calls:
#             func_name = tc.function.name
#             try:
#                 # This creates a dictionary like {"city": "Delhi"}
#                 args = json.loads(tc.function.arguments or "{}")
#             except json.JSONDecodeError:
#                 args = {}

#             if func_name in TOOL_ROUTER:
#                 # 2. CALL the function and pass the arguments
#                 # The ** syntax unpacks {"city": "Delhi"} into get_weather(city="Delhi")
#                 result = TOOL_ROUTER[func_name](**args)
#             else:
#                 result = f"Tool '{func_name}' not found."

#             # 3. Append tool result as a STRING
#             messages.append({
#                 "role": "tool",
#                 "tool_call_id": tc.id,
#                 "name": func_name,
#                 "content": str(result)
#             })

#         # Get final response after tools are processed
#         resp = openai_gemini_client.chat.completions.create(
#             model="gemini-2.5-flash",
#             messages=messages,
#             temperature=0.2,
#         )
#         msg = resp.choices[0].message
#         messages.append(msg) # Add this to history if you want to loop further
        
#         if not msg.tool_calls:
#             break
    
#     # If no tool call was needed, msg.content already contains the answer
#     return msg.content or ""


def run_agent(user_message: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant with Chain of Thought reasoning. "
                "For every request, first analyze the user's intent and explain your "
                "reasoning step-by-step before deciding to use a tool or providing an answer. "
                "If the user asks about weather, explain why you are calling the weather tool."
            ),
        },
        {"role": "user", "content": user_message},
    ]

    while True:
        # First turn: allow tool calls + CoT reasoning
        resp = openai_gemini_client.chat.completions.create(
            model="gemini-2.0-flash", # Ensure you use a CoT-capable model
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
        )
        msg = resp.choices[0].message
        messages.append(msg)

        # 1. Print Reasoning (Chain of Thought)
        # Note: Some SDK versions put reasoning in msg.content, others in msg.reasoning_content
        if msg.content:
            print(f"\n[THOUGHT]:\n{msg.content}")

        # 2. Check if we are done or need to call tools
        if not msg.tool_calls:
            return msg.content or ""

        # 3. Process Tool Calls
        for tc in msg.tool_calls:
            func_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            print(f"[ACTION]: Calling {func_name} with {args}...")
            if func_name in TOOL_ROUTER:
                result = TOOL_ROUTER[func_name](**args)
            else:
                result = f"Tool '{func_name}' not found."

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": func_name,
                "content": str(result)
            })
            print(f"[OBSERVATION]: {result}")


# 5) Demo: pure text vs. tool usage
if __name__ == "__main__":
    # print("\n--- Example: plain prompt (no tools) ---")
    # print(run_agent("hi?"))

    print("\n--- Example: weather (tool call expected) ---")
    print(run_agent("How is the weather at Bengaluru today?"))
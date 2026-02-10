from google import genai
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
import certifi
import json
from pydantic import BaseModel

load_dotenv()
# client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents="Write hi in hindi",
# )
#print(f"Gemini response: {response.text}")

openai_gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# openai_gemini_response = openai_gemini_client.chat.completions.create(
#     model="gemini-2.5-flash",
#     messages=[
#         {   "role": "system",
#             "content": "You are a helpful assistant."
#         },
#         {
#             "role": "user",
#             "content": "Write hello in hindi"
#             #"content": "How gemini api can be used in openai client? answer in 5 lines maximum."
#         }
#     ]
# )

#print(f"Open AI Gemini response: {openai_gemini_response.choices[0].message.content}")


# def get_weather(city:str) -> str:
#     url = f"http://wttr.in/{city.lower()}?format=%C+%t"

#     response = requests.get(url, verify=certifi.where())
#     if response.status_code == 200:
#         print(f"Weather in {city} is {response.text.strip()}")
#     else:        
#         print("Could not retrieve weather data.")


# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_weather",
#             "description": "Get a quick current weather summary for a given city.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "city": {
#                         "type": "string",
#                         "description": "City name, e.g., 'Delhi' or 'Bengaluru'.",
#                     }
#                 },
#                 "required": ["city"],
#                 "additionalProperties": False,
#             },
#         },
#     }
# ]


# TOOL_ROUTER = {
#     "get_weather": get_weather
# }


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
#     )
#     msg = resp.choices[0].message

#     while getattr(msg, "tool_calls", None):
#             for tc in msg.tool_calls:
#                 if tc.type == "function":
#                     func_name = tc.function.name
#                     try:
#                         args = json.loads(tc.function.arguments or "{}")
#                     except json.JSONDecodeError:
#                         args = {}

#                     # Dispatch to the correct local function
#                     if func_name in TOOL_ROUTER:
#                         result = TOOL_ROUTERfunc_name
#                     else:
#                         result = f"Tool '{func_name}' not found."
        

get_weather("Delhi")

# try:
#     openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#     openai_response = openai_client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "user", "content": "Write hi in hindi"}
#         ]
#     )
# except Exception as e:
#     print(f"Error with OpenAI API: {e}")
#     openai_response = None
# finally:

#     if openai_response:
#         print(f"OpenAI response: {openai_response.choices[0].message.content}")
#     else:
#         print("OpenAI response: Not available due to an error.")



from google import genai
from dotenv import load_dotenv
import time
import re
from memory import store_memory, retrieve_memory
import os
import webbrowser

load_dotenv()

def call_model(prompt, api_key):
    if not api_key:
        return "Error: No Gemini API Key provided."
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return f"Error initializing Gemini Client: {str(e)}"
        
    for _ in range(3):
        try:
            res = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return res.text.strip()
        except Exception as e:
            time.sleep(2)
            error_msg = str(e)
            
    return f'API is Unavailable Error. Details: {error_msg}'

def calculator(expression):
    try:
        return str(eval(expression))
    except:
        return "Calculation Error"


def is_math(query):
    return bool(re.search(r'[0-9+\-*/()]', query))

def extract_expr(query):
    match = re.findall(r"[0-9+\-*/().]+", query)
    return "".join(match)


def open_any_website(query):
    if "open" in query:
        site = query.replace("open", "").strip().replace(" ", "")
        url = f"https://www.{site}.com"
        try:
            webbrowser.open(url)
        except:
            pass
        return f"Opening {site}"
    return None

def translate_to_gujarati(text, api_key):
    prompt = f"""
    Translate the following English text into Gujarati.
    Only return translated text, nothing else.
    Text : {text}   
    """
    return call_model(prompt, api_key)


def jarvis(user_input, api_key):
    print("\n🧠 Thinking...")

    web_result = open_any_website(user_input.lower())
    if web_result:
        return web_result

    if is_math(user_input):
        expr = extract_expr(user_input)
        result = calculator(expr)
        store_memory(f"Math: {expr} = {result}")
        return f"The result is {result}"
    memory = retrieve_memory(user_input)

    prompt = f"""
    You are Jarvis AI assistant.

    User history:
    {memory}
    
    Respond naturally and helpfully. Keep answers concise.
    
    User: {user_input} 
    """
    response = call_model(prompt, api_key)
    
    if len(user_input.split()) > 3:
        store_memory(f"User: {user_input}")
        store_memory(f"Jarvis: {response}")

    return response

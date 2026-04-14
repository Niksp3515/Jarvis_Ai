from google import genai
from  dotenv import load_dotenv
import  time
from serpapi import GoogleSearch
from memory import store_memory,retrieve_memory
load_dotenv()

client = genai.Client()
memory = []


def model(prompt):
    for i in range(3):  # retry 3 times
        try:
            response = client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Retry {i + 1} due to error:", e)
            time.sleep(2)

    return "Error: API unavailable"

def Calculator(expression):
    try:
        return str(eval(expression))
    except:
        return 'Error in calculator'

# def ask_agent(user_input):
#     prompt = f"""
#     You are an Ai agent.
#     You can use tools:
#     1. Calculator(expression)
#
#     Rules :
#     - Think step by step
#     - Use tools when needed
#     - Do not generate Observation yourself
#     - Continue until problem is solved
#     - When done , give Final Answer
#
#     Follow this format:
#
#     Thought:
#     Action:
#     Observation: (wait for user)
#
#     User Input: {user_input}
#     """
#     response = model(prompt)
#
#     return response

import  re
# def run_agent(user_input):
#     response = ask_agent(user_input)
#
#     print('Agent Output : \n',response)
#
#     if "Action:" in response:
#         action_line = re.search(r"Action:\s*(.*)", response).group(1)
#
#         match = re.search(r"Calculator\((.*?)\)", action_line)
#
#         if match:
#             expression = match.group(1)
#             result = Calculator(expression)
#         else:
#             result = "Invalid action"
#
#         print("Observation:", result)
#
#         final_prompt = f"""
#     {response}
#
#     Observation: {result}
#
#     Now give Final Answer:
#     """
#         final_response = model.models.generate_content(model='gemini-3-flash-preview', contents=final_prompt)
#         print(final_response.text)
#

# def run_agent_loop(user_input):
#     prompt = f"""
#     You are an AI agent.
#
#     You can use tools:
#     1. Calculator(expression)
#     2. Knowledge(query)
#
#     RULES:
#     - Decide which tool to use
#     - Use Calculator for math
#     - Use Knowledge for factual questions
#     - Do NOT generate Observation
#     - Stop after Action
#
#     Format:
#
#     Thought:
#     Action:
#
#     User Input: {user_input}
#     """
#
#     for step in range(5):
#         response = model(prompt)
#
#         print(f'\nStep {step+1} : \n{response}')
#         if 'Final Answer:' in response:
#             print('\n✅ Done')
#             break
#         if 'Action:' in response:
#             action_line = re.search(r"Action:\s*(.*)", response).group(1)
#
#             #calculator
#             calc_match = re.search(r"Calculator\((.*?)\)", action_line)
#
#             #knowledge
#             know_match = re.search(r"Knowledge\((.*?)\)", action_line)
#             if calc_match:
#                 expression = calc_match.group(1)
#                 result = Calculator(expression)
#             elif know_match:
#                 query = know_match.group(1)
#                 result = knowledge_tool(query)
#             else:
#                 result = 'Invalid Action'
#             print('Observation: ',result)
#             prompt += f"\n{response}\nObservation: {result}\n"

# def search_tool(query):
#     # Mock search (replace with real API later)
#     data = {
#         "who is elon musk": "Elon Musk is CEO of Tesla and SpaceX",
#         "tesla": "Tesla is an electric vehicle company",
#         "spacex": "SpaceX is a space exploration company"
#     }
#     return data.get(query.lower(), f"No results found for {query}")

def search_tool(query):
    import os
    params={
        'q': query,
        'api_key': os.environ.get('SERPAPI_KEY')
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    if 'organic_results' in results:
        snippets=[
            r.get('snippet','')
            for r in results['organic_results'][:3]
        ]
        return ' '.join(snippets)
    return 'No result Found'
# def knowledge_tool(query):
#     data = {
#         "capital of india": "New Delhi",
#         "who is elon musk": "Elon Musk is CEO of Tesla and SpaceX",
#         "python": "Python is a programming language"
#     }
#     return data.get(query.lower(),'No Information Found')

def is_math_query(query):
    return bool(re.search(r"[0-9+\-*/()]", query))


# 🔥 Extract clean expression
def extract_expression(query):
    match = re.findall(r"[0-9+\-*/().]+", query)
    expr = "".join(match)
    return expr if expr else None


def run_agent_loop(user_input):
    if is_math_query(user_input):
        expression = extract_expression(user_input)

        if expression:
            result = Calculator(expression)
            print("\n💬", result)
            store_memory(f"Math result: {result}")
        else:
            print("\n💬 Could not understand the math expression.")

        return
    if any(word in user_input.lower() for word in ["name", "live", "from"]):
        store_memory(f"User info: {user_input}")

    relevant_memory = retrieve_memory(user_input)
    print("\n🔎 Retrieved Memory:\n", relevant_memory)

    prompt = f"""
    You are an AI agent.
    
    Relevant past conversation:
    {relevant_memory}
    
    You can use tools:
    1. Calculator(expression)
    2. Search(query)
    
    CRITICAL RULES:
    
    - You MUST use Calculator for ANY math expression
    - You are NOT allowed to solve math yourself
    - If math is detected → ALWAYS call Calculator
    - If you solve without tool → it is WRONG
    
    - After Observation → MUST give Final Answer
    - NEVER repeat same action
    
    Format:
    
    Thought:
    Action:
    
    User Input: {user_input}
    """
    # 🔁 Loop
    for step in range(3):
        response = model(prompt)
        print(f"\nStep {step + 1}:\n{response}")

        # ✅ Direct response
        if "Action:" not in response:
            final_answer = response.split("\n")[-1]
            print("\n💬", final_answer)
            store_memory(f"Final answer: {final_answer}")
            break

        # 🔍 Extract action
        action_line = re.search(r"Action:\s*(.*)", response).group(1)

        # 🌍 Search tool
        search_match = re.search(r"Search\((.*?)\)", action_line)

        if search_match:
            query = search_match.group(1)
            result = search_tool(query)

            print("Observation:", result)

            prompt += f"\n{response}\nObservation: {result}\nContinue.\n"

        else:
            final_answer = response.split("\n")[-1]
            print("\n💬", final_answer)
            store_memory(f"Final answer: {final_answer}")
            break


while True:
    user_input = input("\nEnter your query: ")

    if user_input.lower() in ["exit", "quit"]:
        print("bye")
        break

    run_agent_loop(user_input)
from google import genai
from  dotenv import load_dotenv
import  time
from serpapi import GoogleSearch
import re
from memory import store_memory,retrieve_memory
load_dotenv()

client = genai.Client()

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


def is_math_query(query):
    return bool(re.search(r"[0-9+\-*/()]", query))


# 🔥 Extract clean expression
def extract_expression(query):
    match = re.findall(r"[0-9+\-*/().]+", query)
    expr = "".join(match)
    return expr if expr else None




def planner_agent(task):
    prompt = f"""
    You are a Planner Agent.

    Break the task into clear, logical steps.

    Task: {task}

    Rules:
    - Keep steps short and actionable
    - Maximum 3–5 steps
    - No explanation
    
    IMPORTANT:
    - If math is involved → write exact expression
    - Do NOT use words like "multiply", "add"
    - Use proper math format
    
    Example:
    Step 1: 5 * 4
    Step 2: (5 * 4) + 10
    
    
    Format:
    Step 1: ...
    Step 2: ...
    Step 3: ...
    """

    return model(prompt)


def executor_agent(step):
    expr_match = re.search(r"Step \d+:\s*(.*)", step)

    if expr_match:
        expression = expr_match.group(1)

        # if math expression → calculate
        if re.search(r"[0-9+\-*/()]", expression):
            return Calculator(expression)

    if any(word in step.lower() for word in ["who", "what", "when", "where"]):
        return search_tool(step)

    prompt = f"""
    Execute this step and give result:

    {step}
    """
    return model(prompt)

def critic_agent(result):
    prompt = f"""
    You are a Critic Agent.

    Improve this answer:
    - Make it clear
    - Remove repetition
    - Keep it concise

    Answer:
    {result}

    Final improved answer:
    """
    return model(prompt)


def store_shared_memory(text):
    store_memory(f"[AGENT MEMORY] {text}")


def run_multi_agent(user_input):
    print('\n🧠 Planning...')
    plan = planner_agent(user_input)
    print(plan)

    steps = [s for s in plan.split("\n") if "Step" in s]

    results = []
    print("\n⚙️ Executing steps...")

    for step in steps:
        if 'Step' in step:
            result = executor_agent(step)
            print(f"\n➡️ {step}")
            print('\nResult : ',result)
            results.append(result)
            store_shared_memory(result)


    combined_result = '\n'.join(results)
    print("\n🧪 Reviewing...")

    final_answer = critic_agent(combined_result)
    print("\n💬 Final Answer:\n", final_answer)

run_multi_agent('Who is Elon Musk and what is his company? Just give short answer maximum 2 to 3 sentences.')

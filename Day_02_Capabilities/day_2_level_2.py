import os
import subprocess
import re
from duckduckgo_search import DDGS

def execute_action(raw_output):
    """The 'Hands': (Unchanged from Level 1)"""
    try:
        blocks = raw_output.split("ACTION:")
        results = []
        for block in blocks:
            if not block.strip():
                continue
            lines = block.strip().split('\n')
            action = lines[0].strip()
            path = content = command = ""
            is_content = False
            
            for line in lines[1:]:
                if line.startswith("PATH:"): path = line.replace("PATH:", "").strip()
                elif line.startswith("CONTENT:"):
                    is_content = True
                    content = line.replace("CONTENT:", "").strip() + "\n"
                elif line.startswith("COMMAND:"): command = line.replace("COMMAND:", "").strip()
                elif is_content: content += line + "\n"
                    
            content = content.strip()
            
            if action == "create_folder":
                os.makedirs(path, exist_ok=True)
                results.append(f"Created folder '{path}'")
            elif action == "create_file":
                directory = os.path.dirname(path)
                if directory: os.makedirs(directory, exist_ok=True)
                with open(path, "w") as f: f.write(content)
                results.append(f"Created file '{path}'")
            elif action == "execute_terminal":
                process = subprocess.run(command, shell=True, capture_output=True, text=True)
                results.append(f"Terminal Output: {process.stdout.strip()}")
                
        return " | ".join(results) if results else "No valid actions found."
    except Exception as e:
        return f"CRITICAL ERROR: {e}"

def chat_with_ollama(system_prompt, user_text):
    process = subprocess.run(
        ["ollama", "run", "llama3", f"{system_prompt}\n\nInput: {user_text}"],
        capture_output=True,
        text=True
    )
    return process.stdout.strip()

def search_the_web(query):
    """The 'Eyes': Physically searches the live internet and returns text."""
    print(f"\n[SYSTEM] Scraping the web for: '{query}'...")
    try:
        results = DDGS().text(query, max_results=3)
        search_text = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return search_text
    except Exception as e:
        return f"Search failed: {e}"

def rudy_dual_brain(user_prompt):
    print(f"\n[USER COMMAND]: {user_prompt}")
    
    # --- BRAIN 1: THE THINKER (NOW WITH A REASONING LOOP) ---
    print("\n--- [BRAIN 1] RUDY IS THINKING ---")
    thinker_system = """You are Rudy, an advanced AI agent. 
    You have the ability to search the live internet if you need current information.
    
    If you need to search the web, output EXACTLY this and nothing else:
    SEARCH: [your search query]
    
    CRITICAL RULES FOR WEB SEARCH:
    1. You must base your final answer STRICTLY on the text provided in the search results.
    2. DO NOT make up information. DO NOT use placeholders like [insert date].
    3. If the search results do not contain the exact answer, you must state: "I could not find accurate live data for this request."
    
    If you have all the information you need, formulate your final creative plan detailing what files or folders to create.""" 

    current_context = user_prompt
    max_loops = 3 # Prevents infinite loops
    
    for i in range(max_loops):
        thinker_thoughts = chat_with_ollama(thinker_system, current_context)
        
        # Check if Rudy decided he needs to search the web
        if "SEARCH:" in thinker_thoughts:
            # Extract the query, search the web, and feed the results back into his brain
            match = re.search(r'SEARCH:\s*(.*)', thinker_thoughts)
            if match:
                query = match.group(1).strip()
                live_data = search_the_web(query)
                print(f"[RUDY OBSERVES LIVE DATA]:\n{live_data}")
                
                # Update his context with the live data and let him think again
                current_context = f"{user_prompt}\n\nWeb Search Results for '{query}':\n{live_data}\n\nNow formulate your final plan based on this live data."
                continue 
        else:
            # Rudy has finished thinking and didn't ask for a search
            print(thinker_thoughts)
            break
            
    # --- BRAIN 2: THE EXECUTOR ---
    print("\n--- [BRAIN 2] EXECUTOR TRANSLATING ---")
    executor_system = """You are an emotionless translation engine. 
    Extract the actions from Rudy's plan and translate them into this EXACT plain text format:
    
    ACTION: create_folder
    PATH: folder_name
    
    ACTION: create_file
    PATH: folder_name/file_name.txt
    CONTENT: file text here
    
    ACTION: execute_terminal
    COMMAND: terminal_command_here
    """
    
    executor_commands = chat_with_ollama(executor_system, thinker_thoughts)
    print(executor_commands)
    
    # --- THE HANDS ---
    print("\n--- [SYSTEM] EXECUTING COMMANDS ---")
    result = execute_action(executor_commands)
    print(f"SUCCESS: {result}")

if __name__ == "__main__":
    # Test Level 2.1: Highly indexed live data
    rudy_dual_brain("Rudy, search the web for the current weather and temperature in Pune. Save a brief summary of the conditions into a file called 'current_weather.txt'.")
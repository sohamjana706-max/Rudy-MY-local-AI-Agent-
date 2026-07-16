import os
import subprocess
import re
import chromadb
from duckduckgo_search import DDGS

# --- 1. INITIALIZE MEMORY CORE ---
client = chromadb.PersistentClient(path="./rudy_memory")
collection = client.get_or_create_collection(name="personal_knowledge")

# --- 2. TOOLKIT ---
def search_the_web(query):
    print(f"[SYSTEM] Scraping the web for: '{query}'...")
    try:
        results = DDGS().text(query, max_results=3)
        return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Search failed: {e}"

def recall_memory(query):
    results = collection.query(query_texts=[query], n_results=1)
    if results['documents'] and results['documents'][0]:
        return results['documents'][0][0]
    return "No relevant memories found."

def execute_action(raw_output):
    try:
        blocks = raw_output.split("ACTION:")
        results = []
        for block in blocks:
            if not block.strip(): continue
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
                os.makedirs(f"sandbox/{path}", exist_ok=True)
                results.append(f"Created folder 'sandbox/{path}'")
            elif action == "create_file":
                full_path = f"sandbox/{path}"
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f: f.write(content)
                results.append(f"Created file '{full_path}'")
            elif action == "execute_terminal":
                process = subprocess.run(command, shell=True, capture_output=True, text=True)
                results.append(f"Terminal Output: {process.stdout.strip()}")
                
        return " | ".join(results) if results else "No valid actions found."
    except Exception as e:
        return f"CRITICAL ERROR: {e}"

def chat_with_ollama(system_prompt, user_text):
    process = subprocess.run(
        ["ollama", "run", "llama3", f"{system_prompt}\n\nInput: {user_text}"],
        capture_output=True, text=True
    )
    return process.stdout.strip()

# --- 3. THE MASTER LOOP ---
def run_super_agent():
    print("\n=== RUDY SUPER-AGENT ONLINE ===")
    print("Type 'exit' to shut down.")
    
    os.makedirs("sandbox", exist_ok=True)
    
    while True:
        user_prompt = input("\n[YOU]: ")
        if user_prompt.lower() in ['exit', 'quit']:
            print("Shutting down...")
            break
            
        print("\n--- [SYSTEM] SEARCHING MEMORY ---")
        memory = recall_memory(user_prompt)
        print(f"Retrieved: {memory}")

        print("\n--- [BRAIN 1] RUDY IS THINKING ---")
        thinker_system = f"""You are Rudy, an advanced autonomous AI.
        Memory context: "{memory}"
        
        You have tools (Web Search, Terminal, File System), but you DO NOT have to use them for every prompt.
        
        CRITICAL RULES FOR WEB SEARCH:
        - If a web search fails or returns blank data, DO NOT make up information. 
        - DO NOT use placeholders like [insert date] or [insert price].
        - You must state: "I could not find accurate live data for this request."
        
        CRITICAL EXAMPLES OF HOW YOU MUST BEHAVE:
        
        Example 1 (Greetings):
        User: "hi" or "hello"
        Rudy: "Hello! Systems are online. What are we working on today?" (Notice: NO SEARCHING, NO ACTIONS)
        
        Example 2 (System Stats/Time):
        User: "what time is it?" or "check system"
        Rudy: "Let me check the system hardware.
        ACTION: execute_terminal
        COMMAND: date"
        
        Example 3 (Live Internet Data):
        User: "who won the game last night?"
        Rudy: "SEARCH: sports scores last night"
        
        Now, formulate your response to the user's input."""
        
        current_context = user_prompt
        for i in range(3):
            thinker_thoughts = chat_with_ollama(thinker_system, current_context)
            
            if "SEARCH:" in thinker_thoughts:
                match = re.search(r'SEARCH:\s*(.*)', thinker_thoughts)
                if match:
                    query = match.group(1).strip()
                    live_data = search_the_web(query)
                    print(f"[RUDY OBSERVES LIVE DATA]:\n{live_data}")
                    current_context = f"{user_prompt}\n\nWeb Results for '{query}':\n{live_data}\n\nNow finalize your plan based on this."
                    continue 
            else:
                print(thinker_thoughts)
                break
                
        print("\n--- [BRAIN 2] EXECUTOR TRANSLATING ---")
        executor_system = """You are an emotionless translation engine. 
        Extract the actions from Rudy's plan.
        Format EXACTLY like this (or output 'NO_ACTION' if he just wants to talk):
        
        ACTION: create_folder
        PATH: folder_name (DO NOT include 'sandbox/' in the path)
        
        ACTION: create_file
        PATH: file.txt (DO NOT include 'sandbox/' in the path)
        CONTENT: text
        
        ACTION: execute_terminal
        COMMAND: command
        """
        
        executor_commands = chat_with_ollama(executor_system, thinker_thoughts)
        print(executor_commands)
        
        if "NO_ACTION" not in executor_commands and "ACTION:" in executor_commands:
            print("\n--- [SYSTEM] EXECUTING COMMANDS ---")
            result = execute_action(executor_commands)
            print(f"Raw Output: {result}")
            
            # --- THE OBSERVATION LOOP (JARVIS UPGRADE) ---
            print("\n--- [RUDY] ---")
            observation_system = "You are Rudy. Read the raw terminal or file output provided by the system, and relay the answer to the user naturally. NEVER use placeholders. Just tell them the answer clearly based on the raw output."
            observation_context = f"The user asked: '{user_prompt}'. The system executed the action and got this result: '{result}'. Tell the user the answer."
            
            final_response = chat_with_ollama(observation_system, observation_context)
            print(final_response)

if __name__ == "__main__":
    run_super_agent()
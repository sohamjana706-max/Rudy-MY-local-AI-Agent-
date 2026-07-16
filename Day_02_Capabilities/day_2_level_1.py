import os
import subprocess

def execute_action(raw_output):
    """The 'Hands': Now upgraded to handle terminal commands safely."""
    try:
        blocks = raw_output.split("ACTION:")
        results = []
        
        for block in blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            action = lines[0].strip()
            path = ""
            content = ""
            command = ""
            is_content = False
            
            # Dirt-simple line-by-line reading
            for line in lines[1:]:
                if line.startswith("PATH:"):
                    path = line.replace("PATH:", "").strip()
                elif line.startswith("CONTENT:"):
                    is_content = True
                    content = line.replace("CONTENT:", "").strip() + "\n"
                elif line.startswith("COMMAND:"):
                    command = line.replace("COMMAND:", "").strip()
                elif is_content:
                    content += line + "\n"
                    
            content = content.strip()
            
            # Tool 1 & 2: File System (From Day 1)
            if action == "create_folder":
                os.makedirs(path, exist_ok=True)
                results.append(f"Created folder '{path}'")
                
            elif action == "create_file":
                directory = os.path.dirname(path)
                if directory:
                    os.makedirs(directory, exist_ok=True)
                with open(path, "w") as f:
                    f.write(content)
                results.append(f"Created file '{path}'")
            
            # Tool 3: NEW TERMINAL CAPABILITY
            elif action == "execute_terminal":
                # This triggers the command directly in your Mac's background terminal
                process = subprocess.run(command, shell=True, capture_output=True, text=True)
                if process.returncode == 0:
                    results.append(f"Terminal Success: {process.stdout.strip()}")
                else:
                    results.append(f"Terminal Error: {process.stderr.strip()}")
                    
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

def rudy_dual_brain(user_prompt):
    print(f"\n[USER COMMAND]: {user_prompt}")
    
    # --- BRAIN 1: THE THINKER ---
    print("\n--- [BRAIN 1] RUDY IS THINKING ---")
    thinker_system = """You are Rudy, an advanced AI agent running on a Mac. 
    Think step-by-step to solve the user's request. 
    You have three tools: create folders, create files, or execute native Mac terminal commands.
    Explain your strategy."""
    
    thinker_thoughts = chat_with_ollama(thinker_system, user_prompt)
    print(thinker_thoughts)
    
    # --- BRAIN 2: THE EXECUTOR ---
    print("\n--- [BRAIN 2] EXECUTOR TRANSLATING ---")
    executor_system = """You are an emotionless translation engine. 
    Extract the actions from Rudy's plan and translate them into this EXACT plain text format:
    
    To create a folder:
    ACTION: create_folder
    PATH: folder_name
    
    To create a file:
    ACTION: create_file
    PATH: folder_name/file_name.txt
    CONTENT: file text here
    
    To run a terminal command:
    ACTION: execute_terminal
    COMMAND: the_mac_terminal_command_here
    
    Do not add any other words."""
    
    executor_commands = chat_with_ollama(executor_system, thinker_thoughts)
    print(executor_commands)
    
    # --- THE HANDS ---
    print("\n--- [SYSTEM] EXECUTING COMMANDS ---")
    result = execute_action(executor_commands)
    print(f"SUCCESS: {result}")

if __name__ == "__main__":
    # The ultimate test for Level 1:
    # 1. Ask Rudy to check your Mac's uptime (read-only terminal command).
    # 2. Ask Rudy to physically make your Mac speak out loud (interactive terminal command).
    test_prompt = "Rudy, check how long my Mac has been running using the 'uptime' command. Then, make my Mac physically speak the words 'System control is online' using the Mac 'say' command."
    rudy_dual_brain(test_prompt)
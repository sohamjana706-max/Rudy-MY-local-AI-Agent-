import os
import subprocess

def execute_file_command(raw_output):
    """The 'Hands': Safely executes the clean text provided by the Executor."""
    try:
        # Split by ACTION: so we can process multiple commands if Rudy wants to make several files
        blocks = raw_output.split("ACTION:")
        results = []
        
        for block in blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            action = lines[0].strip()
            path = ""
            content = ""
            is_content = False
            
            for line in lines[1:]:
                if line.startswith("PATH:"):
                    path = line.replace("PATH:", "").strip()
                elif line.startswith("CONTENT:"):
                    is_content = True
                    content = line.replace("CONTENT:", "").strip() + "\n"
                elif is_content:
                    content += line + "\n"
                    
            content = content.strip()
            
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
                
        return " | ".join(results) if results else "No valid actions found."
            
    except Exception as e:
        return f"CRITICAL ERROR: {e}"

def chat_with_ollama(system_prompt, user_text):
    """A helper function so we can easily call the local Llama 3 model multiple times."""
    process = subprocess.run(
        ["ollama", "run", "llama3", f"{system_prompt}\n\nInput: {user_text}"],
        capture_output=True,
        text=True
    )
    return process.stdout.strip()

def rudy_dual_brain(user_prompt):
    print(f"\n[USER COMMAND]: {user_prompt}")
    
    # ---------------------------------------------------------
    # BRAIN 1: THE THINKER (Creative, Self-Improving, Verbose)
    # ---------------------------------------------------------
    print("\n--- [BRAIN 1] RUDY IS THINKING ---")
    thinker_system = """You are Rudy, an incredibly smart, creative AI assistant. 
    The user will give you a task. Think step-by-step about how to solve it. 
    Decide what folders or files need to be created, and what the content should be. 
    Be highly creative, write out your thoughts, and explain your strategy. You have a mind of your own."""
    
    thinker_thoughts = chat_with_ollama(thinker_system, user_prompt)
    print(thinker_thoughts)
    
    # ---------------------------------------------------------
    # BRAIN 2: THE EXECUTOR (Strict, Emotionless Translator)
    # ---------------------------------------------------------
    print("\n--- [BRAIN 2] EXECUTOR TRANSLATING ---")
    executor_system = """You are an emotionless translation engine. 
    Read the creative plan provided by Rudy. 
    Extract ONLY the file system actions and translate them into this EXACT plain text format:
    
    ACTION: create_folder
    PATH: folder_name
    
    ACTION: create_file
    PATH: folder_name/file_name.txt
    CONTENT: The text inside the file
    
    Do not add any other words. Only output the ACTION, PATH, and CONTENT lines."""
    
    executor_commands = chat_with_ollama(executor_system, thinker_thoughts)
    print(executor_commands)
    
    # ---------------------------------------------------------
    # THE HANDS: PYTHON EXECUTION
    # ---------------------------------------------------------
    print("\n--- [SYSTEM] EXECUTING COMMANDS ---")
    result = execute_file_command(executor_commands)
    print(f"SUCCESS: {result}")

if __name__ == "__main__":
    # Let's give Rudy a creative prompt so you can see his mind at work
    rudy_dual_brain("Rudy, I need a new project folder called 'Indie_Film_Marketplace'. Inside it, create a file called 'brainstorm.txt' and write down 3 creative features for an app that connects indie directors with equipment rentals.")
import os
import subprocess
import re

def execute_file_command(raw_output):
    """The 'Hands': Forcefully extracts commands using Regex, ignoring all formatting errors."""
    try:
        # re.DOTALL makes Regex ignore line breaks entirely. It will find the text no matter what.
        action_match = re.search(r'(.*?)', raw_output, re.DOTALL)
        path_match = re.search(r'(.*?)', raw_output, re.DOTALL)
        
        if not action_match or not path_match:
            return "Error: Could not find  and  tags in Rudy's output."
            
        action = action_match.group(1).strip()
        path = path_match.group(1).strip()
        
        if action == "create_folder":
            os.makedirs(path, exist_ok=True)
            return f"Created folder '{path}'"
            
        elif action == "create_file":
            content_match = re.search(r'(.*?)', raw_output, re.DOTALL)
            content = content_match.group(1).strip() if content_match else ""
            
            # Safety check: ensure the folder exists before writing
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)
                
            with open(path, "w") as f:
                f.write(content)
            return f"Created file '{path}'"
            
    except Exception as e:
        return f"CRITICAL ERROR: {e}"

def rudy_file_agent(user_prompt):
    """The 'Brain': Instructs Rudy to use indestructible XML tags."""
    print(f"\n[USER COMMAND]: {user_prompt}")
    print("Rudy is processing...")
    
    system_prompt = """You are Rudy, an AI agent controlling a macOS file system. 
    You must respond ONLY using the exact XML tags below. No conversational text.
    
    To create a folder, output: 
    create_folder
    folder_name
    
    To create a file, output: 
    create_file
    file_name
    file_text
    """

    process = subprocess.run(
        ["ollama", "run", "llama3", f"{system_prompt}\nUser Request: {user_prompt}"],
        capture_output=True,
        text=True
    )
    
    raw_output = process.stdout.strip()
    print(f"[RUDY'S THOUGHT PROCESS]:\n{raw_output}")
    
    result = execute_file_command(raw_output)
    print(f"[SYSTEM EXECUTION]: SUCCESS: {result}")

if __name__ == "__main__":
    rudy_file_agent("Rudy, create a folder called 'Mission_Control'.")
    rudy_file_agent("Now create a file inside 'Mission_Control' called 'status.txt' and write 'All systems go.' inside it.")
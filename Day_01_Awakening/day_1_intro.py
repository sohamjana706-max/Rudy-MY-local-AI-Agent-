import subprocess

def wake_up_agent():
    # The prompt instructing the AI who it is
    system_prompt = "You are a highly advanced local AI assistant running on an Apple M4 chip. Introduce yourself in one punchy, confident sentence."
    
    print("Booting local engine...")
    
    # This Python script autonomously triggers the Ollama engine in your terminal
    # using the exact command: 'ollama run llama3' 
    process = subprocess.run(
        ["ollama", "run", "llama3", system_prompt],
        capture_output=True,
        text=True
    )
    
    # Observe and Print the Output
    print("\n--- SYSTEM RESPONSE ---")
    print(process.stdout)

if __name__ == "__main__":
    wake_up_agent()
import chromadb
import subprocess
import os

# 1. INITIALIZE THE MEMORY CORE
# This creates a hidden folder called 'rudy_memory' to permanently store vectors
client = chromadb.PersistentClient(path="./rudy_memory")
collection = client.get_or_create_collection(name="personal_knowledge")

def teach_rudy(text, memory_id):
    """Forces Rudy to memorize a piece of text permanently."""
    collection.upsert(
        documents=[text],
        ids=[memory_id]
    )
    print(f"[MEMORY SAVED]: {text}")

def recall_memory(query):
    """Searches the database for the most relevant memory."""
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    # If he found a memory, return it. Otherwise, return nothing.
    if results['documents'] and results['documents'][0]:
        return results['documents'][0][0]
    return "No relevant memories found."

def chat_with_ollama(system_prompt, user_text):
    process = subprocess.run(
        ["ollama", "run", "llama3", f"{system_prompt}\n\nInput: {user_text}"],
        capture_output=True,
        text=True
    )
    return process.stdout.strip()

def rudy_memory_agent(user_prompt):
    print(f"\n[USER COMMAND]: {user_prompt}")
    
    # --- THE RECALL PHASE ---
    print("\n--- [SYSTEM] SEARCHING MEMORY CORE ---")
    recalled_data = recall_memory(user_prompt)
    print(f"Retrieved: {recalled_data}")
    
    # --- THE THINKING PHASE ---
    system_prompt = f"""You are Rudy, an AI agent with long-term memory.
    The system has retrieved a memory from your database that might help answer the user.
    
    RECALLED MEMORY: "{recalled_data}"
    
    If the memory contains the answer, use it. If not, just answer normally."""
    
    response = chat_with_ollama(system_prompt, user_prompt)
    print(f"\n[RUDY]: {response}")

if __name__ == "__main__":
    print("\n=== PHASE 1: TEACHING ===")
    # We inject a highly specific, fictional fact into his vector database
    teach_rudy("Protocol Omega is the secret override code, which is 99-X-Ray.", "secret_code")
    teach_rudy("The user's ultimate goal is to become a pilot.", "career_goal")
    
    print("\n=== PHASE 2: TESTING ===")
    # We test if he can pull the correct memory mathematically
    rudy_memory_agent("Rudy, what is the secret override code?")
    rudy_memory_agent("What is my long-term career goal outside of tech?")
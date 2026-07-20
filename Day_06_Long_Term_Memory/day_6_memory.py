import os
import chromadb
from chromadb.config import Settings

# --- INITIALIZE CHROMA VECTOR DATABASE Locally ---
# This creates a 'memory_vault' directory right on your Mac storage
db_path = os.path.join(os.path.dirname(__file__), "memory_vault")
chroma_client = chromadb.PersistentClient(path=db_path)

# Create or fetch our specialized voice chat logs collection
memory_collection = chroma_client.get_or_create_collection(name="jarvis_audio_logs")

def save_interaction_to_memory(user_speech, rudy_response):
    """Converts the voice conversation string into vectors and stores it permanently."""
    if not user_speech.strip(): return
    
    # Structure the memory block
    combined_text = f"User said: {user_speech} | Rudy responded: {rudy_response}"
    
    # Generate a simple unique index tracking point using current timestamps
    import time
    log_id = f"log_{int(time.time())}"
    
    # ChromaDB natively handles embedding generation on text strings under the hood
    memory_collection.add(
        documents=[combined_text],
        ids=[log_id],
        metadatas=[{"timestamp": time.time()}]
    )
    print(f"\n[MEMORY SYSTEM]: Interaction logged successfully under ID: {log_id}")

def query_relevant_memory(current_input):
    """Queries the database to fetch past contextual interactions matching current topic."""
    if not current_input.strip(): return ""
    
    # Search the collection for the closest mathematical vector matches
    results = memory_collection.query(
        query_texts=[current_input],
        n_results=2 # Grab the top 2 most relevant historical milestones
    )
    
    # Format and extract the results nicely for our prompt engine
    if results and results['documents'] and results['documents'][0]:
        past_contexts = "\n".join(results['documents'][0])
        return f"\n[PAST HISTORICAL CONTEXT RETRIEVED]:\n{past_contexts}\n"
    
    return ""

if __name__ == "__main__":
    # Test our baseline vector components directly
    print("[TESTING VAULT]: Injecting sample milestone data...")
    save_interaction_to_memory("I am working on building my local AI agent project today", "Understood sir, I will remember our developmental setup.")
    
    print("\n[TESTING QUERY]: Searching vector weights...")
    recalled = query_relevant_memory("What did we say about the AI agent project?")
    print(recalled)
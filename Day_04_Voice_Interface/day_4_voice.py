import sys
import datetime
import re
import subprocess
import time

# --- PATH & AGENT ENGINE BRIDGES ---
sys.path.append('../Day_03_SuperAgent')
sys.path.append('../Day_06_Long_Term_Memory')  # Bridge to your memory folder

from day_3_master import chat_with_ollama, recall_memory, execute_action
from day_6_memory import save_interaction_to_memory, query_relevant_memory  # Memory Vault Tools
import speech_recognition as sr
import pyttsx3

# --- 1. VOICE ENGINE ---
engine = pyttsx3.init()
def speak(text):
    print(f"\n[RUDY]: {text}")
    engine.say(text)
    engine.runAndWait()

# --- 2. LISTENER ENGINE ---
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[LISTENING...]")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"[YOU]: {text}")
        return text
    except:
        return ""

# --- 3. INTENT ROUTER (The Efficiency Layer) ---
def get_intent(user_input):
    ui = user_input.lower()
    if any(w in ui for w in ["time", "date"]): return "GET_TIME"
    if any(w in ui for w in ["battery", "disk", "space", "storage"]): return "SYSTEM_STATS"
    if any(w in ui for w in ["open", "launch", "play"]): return "LAUNCH_APP"
    return "THINKER_BRAIN"

# --- 4. VOICE INTERFACE LOOP ---
def run_voice_agent():
    speak("Systems online. Reflex layer active.")
    while True:
        user_input = listen()
        if not user_input: continue
        if "stop" in user_input.lower(): 
            speak("Shutting down.")
            break
            
        # ROUTING
        intent = get_intent(user_input)
        
        if intent == "GET_TIME":
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"Sir, the time is {now}.")
            
        elif intent == "SYSTEM_STATS":
            ui_lower = user_input.lower()
            if "battery" in ui_lower:
                speak("Checking battery status, sir.")
                stats = execute_action("ACTION: execute_terminal\nCOMMAND: pmset -g batt")
                match = re.search(r'(\d+%)', stats)
                if match:
                    speak(f"Your battery is currently at {match.group(1)}.")
                else:
                    speak("I am unable to parse the battery status string.")
            else:
                speak("Checking local storage space.")
                stats = execute_action("ACTION: execute_terminal\nCOMMAND: df -h")
                speak(f"System storage status: {stats[:50]}...") 
                
        elif intent == "LAUNCH_APP":
            ui_lower = user_input.lower()
            
            # Smart extraction: Map media phrases directly to the player framework
            if any(w in ui_lower for w in ["spotify", "play", "song", "music"]):
                target_app = "Spotify"
            elif "safari" in ui_lower:
                target_app = "Safari"
            else:
                target_app = None
            
            if target_app:
                speak(f"Opening {target_app} now, sir.")
                execute_action(f"ACTION: execute_terminal\nCOMMAND: open -a {target_app}")
                
                # --- THE HARDWARE WAKE CUSHION ---
                # Give the macOS application loop 2.5 seconds to fully initialize cleanly
                time.sleep(2.5)
                
                # Dynamic track extraction logic
                if "play" in ui_lower and len(ui_lower.split("play")) > 1:
                    track_name = ui_lower.split("play")[1].strip()
                    # Clean out common noise words from the track name string
                    for noise in ["spotify", "music", "song", "the song"]:
                        track_name = track_name.replace(noise, "").strip()
                        
                    if track_name:
                        speak(f"Attempting to queue up {track_name} for you.")
            else:
                speak("Which application would you like me to open, sir?")
            
        else: # THINKER_BRAIN (Memory Locked and Loaded)
            speak("Thinking...")
            
            # Step A: Query ChromaDB local space for matching historical logs [cite: 401]
            past_memories = query_relevant_memory(user_input)
            
            # Step B: Construct context-injected payload prompt [cite: 401]
            system_instructions = "You are Rudy, an efficient AI assistant with persistent long-term memory logs."
            if past_memories:
                user_prompt = f"{past_memories}\n\nCurrent User Query: {user_input}"
            else:
                user_prompt = user_input
            
            # Step C: Complete local LLM generation loop
            response = chat_with_ollama(system_instructions, user_prompt)
            speak(response)
            
            # Step D: Save this exchange to memory storage for next time [cite: 401]
            save_interaction_to_memory(user_input, response)

if __name__ == "__main__":
    run_voice_agent()
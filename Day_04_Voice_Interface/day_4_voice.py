import sys
import datetime
sys.path.append('../Day_03_SuperAgent')
from day_3_master import chat_with_ollama, recall_memory, execute_action
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
    if any(w in ui for w in ["battery", "disk", "space"]): return "SYSTEM_STATS"
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
            speak("Checking system status.")
            # We call your Super-Agent's tool executor directly!
            stats = execute_action("ACTION: execute_terminal\nCOMMAND: df -h")
            speak(f"System status: {stats[:50]}...") # Just reading the first bit
            
        else: # THINKER_BRAIN
            speak("Thinking...")
            # Here we call the logic we built in Day 3
            response = chat_with_ollama("You are Rudy, an efficient AI assistant.", user_input)
            speak(response)

if __name__ == "__main__":
    run_voice_agent()
import speech_recognition as sr
import subprocess
import os
import sys

def run_daemon():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    # Advanced Noise Calibration
    # Adjust dynamic energy thresholds to filter room hums
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300  
    
    venv_python = sys.executable 
    agent_path = "../Day_04_Voice_Interface/day_4_voice.py"
    
    print("[DAEMON]: System calibrated. Listening for wake word...")
    
    while True:
        try:
            with mic as source:
                # Samples background noise dynamically to keep tracking accurate
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                audio = recognizer.listen(source, phrase_time_limit=3)
            
            command = recognizer.recognize_google(audio).lower()
            print(f"[DAEMON]: Heard raw string: '{command}'")
            
            # Expanded phonetic safety net to catch transcription errors
            wake_words = [
                "rudy", "rudi", "ruby", "ruddy", "roody", 
                "routine", "riddle", "ready", "dude", "root"
            ]
            
            if any(word in command for word in wake_words):
                print("[DAEMON]: Wake word matched! Releasing audio hardware...")
                print(f"[DAEMON]: Launching Agent via {agent_path}")
                
                # Execute the active main voice interface loop natively
                subprocess.run([venv_python, agent_path])
                
                print("\n[DAEMON]: Agent session ended. Returning to background sleep...")
                
        except sr.UnknownValueError:
            # Silence log spam when the room is quiet
            continue
        except Exception as e:
            print(f"[DAEMON] Error: {e}")
            continue

if __name__ == "__main__":
    run_daemon()
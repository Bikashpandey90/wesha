import os
import re
import numpy as np
import speech_recognition as sr
from dotenv import load_dotenv
from elevenlabs import  ElevenLabs,play
import google.generativeai as genai

# Load environment variables
load_dotenv()

# ========== [1] API Key Setup ==========
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client= ElevenLabs(
    api_key=os.getenv('ELEVEN_LABS_API_KEY')
)

# ========== [2] Gemini Model Setup ==========
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

# ========== [3] Speech Recognizer Setup ==========
r = sr.Recognizer()
language = 'en'
name = "Bikash"

# ========== [4] Greetings ==========
greetings = [
    f"whats up master {name}",
    "yeah?",
    "Well, hello there! How's it going today?",
    f"Ahoy there, Captain {name}! How's the ship sailing?",
    "How can I help?",
    "How's it going my man!",
    f"Bonjour, Monsieur {name}! Comment ça va? Wait, why the hell am I speaking French?"
]

# ========== [5] Helper: Clean Markdown Text ==========
def clean_text(text):
    return re.sub(r'[*_~`]', '', text)

# ========== [6] Speak with ElevenLabs ==========
def say(text):
    text = clean_text(text)
    try:
        # audio = generate(text=text, voice="Bella", model="eleven_multilingual_v1")
        # play(audio)
        audio= client.text_to_speech.convert(
            text=text,
              voice_id="Bel2OEeJcYw2f3bWMzzjVMUla",
                 model_id="eleven_multilingual_v2",
                 output_format="mp3_44100_128",
        )
        play(audio)
    except Exception as e:
        print("Error in ElevenLabs playback:", e)

# ========== [7] Get Response from Gemini ==========
def get_gemini_response(text):
    try:
        response = chat.send_message(text)
        return response.text
    except Exception as e:
        return "Sorry, I couldn't connect to Gemini right now."

# ========== [8] Wake Word Listener ==========
def listen_for_wake_word(source):
    print("Listening for 'hello'...")
    while True:
        try:
            audio = r.listen(source, timeout=30, phrase_time_limit=5)
            text = r.recognize_google(audio)
            print(f"Heard: {text}")
            if "hello" in text.lower():
                print("Wake word detected.")
                say(np.random.choice(greetings))
                listen_and_respond(source)
                break
        except sr.WaitTimeoutError:
            print("No sound detected. Restarting wake word listener...")
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print("Unexpected error in wake listener:", e)

# ========== [9] Main Conversation Loop ==========
def listen_and_respond(source):
    try:
        from playsound import playsound
    except:
        playsound = None

    if playsound:
        try:
            playsound("listen_chime.mp3")
        except:
            pass

    while True:
        print("Listening...")
        try:
            audio = r.listen(source, timeout=15, phrase_time_limit=10)
            text = r.recognize_google(audio)
            print(f"You said: {text}")

            if not text:
                continue

            response = get_gemini_response(text)
            print("Gemini:", response.replace("*",""))
            say(response.replace("*",""))

            if playsound:
                try:
                    playsound("listen_chime.mp3")
                except:
                    pass

        except sr.WaitTimeoutError:
            print("Timeout: no speech detected.")
            if playsound:
                try:
                    playsound("error.mp3")
                except:
                    pass
            listen_for_wake_word(source)
            break

        except sr.UnknownValueError:
            print("Didn't catch that. Listening again...")
            if playsound:
                try:
                    playsound("error.mp3")
                except:
                    pass
            listen_for_wake_word(source)
            break

        except Exception as e:
            print("Error during listening loop:", e)
            break

# ========== [10] Start Program ==========
if __name__ == "__main__":
    print("🎤 Wesha Voice Assistant is running...")
    with sr.Microphone() as source:
        listen_for_wake_word(source)

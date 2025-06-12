import os
import google.generativeai as genai
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import numpy as np
from gtts import gTTS
from playsound import playsound

load_dotenv()

# Set your Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Ensure this is set in your .env file
model = genai.GenerativeModel("gemini-2.0-flash")

# Speech & Voice
r = sr.Recognizer()
tts_engine = 'gtts'  # or 'pyttsx3'

engine = pyttsx3.init()
voice = engine.getProperty('voices')[2]
engine.setProperty('voice', voice.id)

language = 'en'
name = "Bikash"
greetings = [
    f"whats up master {name}",
    "yeah?",
    "Well, hello there! How's it going today?",
    f"Ahoy there, Captain {name}! How's the ship sailing?",
    "How can I help?",
    "How's it going my man!",
    f"Bonjour, Monsieur {name}! Comment ça va? Wait, why the hell am I speaking French?"
]

# Initialize Gemini chat session
chat = model.start_chat(history=[])

# Wake word listener
def listen_for_wake_word(source):
    print("Listening for 'hello'...")
    while True:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            if "hello" in text.lower():
                print("Wake word detected.")
                if tts_engine == 'pyttsx3':
                    engine.say(np.random.choice(greetings))
                    engine.runAndWait()
                else:
                    greet = gTTS(text=np.random.choice(greetings), lang=language)
                    greet.save('response.mp3')
                    playsound('response.mp3')
                listen_and_respond(source)
                break
        except sr.UnknownValueError:
            pass

# Gemini-based response function
def get_gemini_response(text):
    response = chat.send_message(text)
    return response.text

# Main interaction
def listen_and_respond(source):
    playsound("listen_chime.mp3")
    while True:
        print("Listening...")
        audio = r.listen(source, timeout=15)
        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            if not text:
                continue

            response_text = get_gemini_response(text)
            print(response_text)

            if tts_engine == 'pyttsx3':
                engine.say(response_text)
                engine.runAndWait()
            elif tts_engine == 'gtts':
                # cleaned_response = response_text.replace("*", "")
                resp = gTTS(text=response_text.replace("*", ""), lang=language)
                if os.path.exists("response.mp3"):
                     os.remove("response.mp3")
                     resp.save("response.mp3")
                playsound('response.mp3')

            playsound("listen_chime.mp3")

        except sr.UnknownValueError:
            playsound("error.mp3")
            print("Silence found, shutting up, listening...")
            listen_for_wake_word(source)
            break
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            engine.say(f"Could not request results; {e}")
            engine.runAndWait()
            listen_for_wake_word(source)
            break

# Start with microphone
with sr.Microphone() as source:
    listen_for_wake_word(source)

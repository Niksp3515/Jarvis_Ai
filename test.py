import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os

# 🔹 Speak Function
def speak(text):
    print("🔊 AI:", text)

    tts = gTTS(text=text, lang='en')
    filename = "voice.mp3"

    tts.save(filename)
    playsound(filename)

    os.remove(filename)


# 🔹 Listen Function
def listen():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print("🧑 You:", text)
        return text
    except:
        print("❌ Could not understand")
        return ""


# 🔥 Conversation Flow
speak("Hello, my name is Jarvis")

user_input = listen()

if user_input:
    speak("You said " + user_input)

speak("This is perfect. Bye")
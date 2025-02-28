import speech_recognition as sr
import webbrowser
import requests
import pygame
import os
import google.generativeai as genai
from gtts import gTTS

# 🔹 Load API keys securely from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Set this in your system or use a .env file
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# 🔹 Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# 🔹 Initialize recognizer
recognizer = sr.Recognizer()

# 🔹 Sample music library (expand as needed)
musicLibrary = {
    "believer": "https://www.youtube.com/watch?v=7wtfhZwyrcc",
    "faded": "https://www.youtube.com/watch?v=60ItHLz5WEA",
}

def speak(text):
    """Convert text to speech using gTTS and play the audio."""
    tts = gTTS(text)
    tts.save('temp.mp3')

    pygame.mixer.init()
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.delay(100)

    pygame.mixer.quit()
    os.remove("temp.mp3")

def aiProcess(command):
    """Process user command using Google Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(command)
        return response.text
    except Exception as e:
        return "Sorry, I couldn't process that request."

def processCommand(command):
    """Process recognized commands and take actions."""
    command = command.lower()

    if "open google" in command:
        webbrowser.open("https://google.com")
    elif "open facebook" in command:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in command:
        webbrowser.open("https://linkedin.com")
    elif command.startswith("play"):
        song = command.split(" ")[1]
        link = musicLibrary.get(song)
        if link:
            webbrowser.open(link)
        else:
            speak("Sorry, I couldn't find that song.")
    elif "news" in command:
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}")
            if r.status_code == 200:
                articles = r.json().get('articles', [])
                for article in articles[:5]:  # Read only top 5 headlines
                    speak(article['title'])
        except Exception as e:
            speak("Sorry, I couldn't fetch news.")
    else:
        response = aiProcess(command)
        speak(response)

if __name__ == "__main__":
    speak("Initializing Jarvis with Google Gemini AI...")
    
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                word = recognizer.recognize_google(audio).lower()

                if "jarvis" in word:
                    speak("Yes?")
                    with sr.Microphone() as source:
                        audio = recognizer.listen(source, timeout=5)
                        command = recognizer.recognize_google(audio)
                        processCommand(command)

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError:
            print("Check internet connection")
        except Exception as e:
            print(f"Error: {e}")

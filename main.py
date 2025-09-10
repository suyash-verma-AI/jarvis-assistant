import os
import requests
import webbrowser
import wikipedia
import pyjokes
import pygame
import pyttsx3
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import musicLibrary

# ---------------------- CONFIG ----------------------
NEWS_API_KEY = "YOUR_NEWS_API_KEY"
WEATHER_API_KEY = "YOUR_WEATHER_API_KEY"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

genai.configure(api_key=GEMINI_API_KEY)

recognizer = sr.Recognizer()
engine = pyttsx3.init()

# ---------------------- SPEAK FUNCTION ----------------------


def speak(text: str):
    """Convert text to speech using gTTS + pygame."""
    try:
        tts = gTTS(text)
        tts.save("temp.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("temp.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove("temp.mp3")
    except Exception as e:
        print("Speech Error:", e)

# ---------------------- GEMINI AI ----------------------


def aiProcess(command: str) -> str:
    """Get AI-generated response from Google Gemini."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([
            "You are a virtual assistant named Jarvis. Reply short and precise.",
            command
        ])
        return response.text
    except Exception as e:
        print("Gemini Error:", e)
        return "Sorry, I couldn't process that."

# ---------------------- WEATHER ----------------------


def get_weather(city: str) -> str:
    """Fetch live weather data for a city."""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        return f"The current temperature in {city} is {temp}°C with {condition}."
    except Exception as e:
        print("Weather API Error:", e)
        return "Sorry, I couldn't fetch the weather right now."

# ---------------------- COMMAND HANDLER ----------------------


def processCommand(c: str):
    """Process user voice command and perform action."""
    c_lower = c.lower().strip()

    # --- Websites
    if "open google" in c_lower:
        webbrowser.open("https://google.com")
    elif "open facebook" in c_lower:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c_lower:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c_lower:
        webbrowser.open("https://linkedin.com")

    # --- Music
    elif c_lower.startswith("play"):
        song = c_lower.replace("play", "").strip()
        if song in [key.lower() for key in musicLibrary.music]:
            for key, link in musicLibrary.music.items():
                if key.lower() == song:
                    webbrowser.open(link)
                    speak(f"Playing {key}")
                    break
        else:
            speak(f"Sorry, I don't have {song}. Searching on YouTube...")
            webbrowser.open(
                f"https://www.youtube.com/results?search_query={song}")

    # --- News
    elif "news" in c_lower:
        try:
            r = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}")
            r.raise_for_status()
            data = r.json()
            articles = data.get("articles", [])
            if not articles:
                speak("Sorry, I couldn't find any news right now.")
            else:
                speak("Here are the top 5 headlines.")
                for article in articles[:5]:
                    speak(article.get("title", ""))
        except Exception as e:
            print("News API Error:", e)
            speak("Sorry, I am unable to fetch news at the moment.")

    # --- Weather
    elif "weather in" in c_lower:
        city = c_lower.split("weather in")[-1].strip()
        report = get_weather(city)
        speak(report)

    # --- Calculator
    elif any(op in c_lower for op in ["plus", "minus", "times", "multiplied", "divided", "/", "+", "-", "*"]):
        try:
            expression = c_lower.replace("plus", "+").replace("minus", "-")\
                                .replace("times", "*").replace("multiplied", "*")\
                                .replace("divided", "/").replace("by", "")
            result = eval(expression)
            speak(f"The answer is {result}")
        except:
            speak("Sorry, I couldn't calculate that.")

    # --- Wikipedia
    elif "tell me about" in c_lower:
        topic = c_lower.replace("tell me about", "").strip()
        try:
            summary = wikipedia.summary(topic, sentences=2)
            speak(summary)
        except:
            speak("Sorry, I couldn't find information on that topic.")

    # --- Jokes
    elif "joke" in c_lower:
        joke = pyjokes.get_joke()
        speak(joke)

    # --- Apps (local paths → adjust as needed)
    elif "open whatsapp" in c_lower:
        os.startfile(r"C:\Users\Suyash\OneDrive\Desktop\WhatsApp.lnk")
    elif "open spotify" in c_lower:
        os.startfile(r"C:\Users\Suyash\OneDrive\Desktop\Spotify.lnk")
    elif "open canva" in c_lower:
        os.startfile(r"C:\Users\Suyash\OneDrive\Desktop\Canva.lnk")

    # --- Else → AI
    else:
        output = aiProcess(c)
        speak(output)


# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening for wake word...")
                audio = recognizer.listen(
                    source, timeout=10, phrase_time_limit=5)

            word = recognizer.recognize_google(audio)
            print("Heard:", word)

            if "jarvis" in word.lower():
                speak("Yes?")
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    print("Jarvis Active... Listening for command")
                    audio = recognizer.listen(
                        source, timeout=10, phrase_time_limit=8)
                    command = recognizer.recognize_google(audio)
                    print("Command:", command)
                    processCommand(command)

        except Exception as e:
            print("Error:", e)

import google.generativeai as genai
import os


api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "❌ GEMINI_API_KEY not found! Set it as an environment variable.")


genai.configure(api_key=api_key)


model = genai.GenerativeModel("gemini-1.5-flash")


response = model.generate_content([
    "You are a virtual assistant named Jarvis skilled in general tasks like Alexa and Google Cloud.",
    "what is coding"
])


print("🤖 Jarvis:", response.text)

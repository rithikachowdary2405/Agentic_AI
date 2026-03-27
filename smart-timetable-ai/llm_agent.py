import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def ask_llm(question):
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"AI error: {e}"
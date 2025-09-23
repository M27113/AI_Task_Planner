import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
import spacy

load_dotenv()

# Initialize spaCy NLP for city/state/country extraction
nlp = spacy.load("en_core_web_sm")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
TAVILY_KEY = os.getenv("TAVILY_API_KEY")


# ---------- Location Extraction ----------
def extract_location(goal: str) -> str:
    """ Detect city/state/country from goal using NLP.
        Returns the first GPE (Geopolitical Entity) found, or empty string if none."""
    doc = nlp(goal)
    for ent in doc.ents:
        if ent.label_ == "GPE":  # Geopolitical entity (city, state, country)
            return ent.text
    return ""  # No Location found


# ---------- API Calls ----------
def get_weather(location: str) -> str:
    """ Fetch current weather if a location is detected.
        Returns empty string if no location or API error occurs"""
    if not location:
        return ""  
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={OPENWEATHER_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The weather in {location} is {desc} with temperature {temp}°C."
    except requests.exceptions.RequestException:
        return ""  # silently skip if API fails


def search_web(query: str) -> str:
    """ Fetch top 3 search results from Tavily API.
        Returns concatenated snippets or empty string if API fails"""
    try:
        url = "https://api.tavily.com/search"
        headers = {"Authorization": f"Bearer {TAVILY_KEY}"}
        params = {"q": query, "num": 3}
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        results = response.json().get("results", [])
        snippets = [r.get("snippet", "") for r in results]
        return "\n".join(snippets) if snippets else ""
    except requests.exceptions.RequestException:
        return ""


# ---------- LLM Call ----------
def call_llm(prompt: str) -> str:
    """ Calls OpenAI GPT-4o Mini API with the given prompt.
        Returns the text output."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()


# ---------- Planner ----------
def generate_plan(goal: str) -> str:
    """ Generate day-by-day plan enriched with search info and optional weather.
        Includes optional weather info and web search context."""
    # Extract location using spaCy
    location = extract_location(goal)

    # Fetch weather only if location is detected
    weather_info = get_weather(location) if location else ""

    # Fetch search info
    search_info = search_web(goal)

    # LLM prompt
    prompt = f"""
    
    Goal: {goal}
    {'Weather info: ' + weather_info if weather_info else ''}
    Additional info: {search_info}
    
    You are an AI task planner. Your job is to convert a natural language goal into a structured, day-by-day actionable plan.
    
    Instructions:
    - Convert the user's goal into a clear, actionable day-by-day plan.
    - Include weather forecast conditions for each day, based on the current weather if a location is detected.
    - Please generate a clear, day-by-day actionable plan. Use emoji-friendly headings for each day:

        - ☀️ Morning
        - 🌞 Afternoon
        - 🌙 Evening

    - Include meaningful numbered steps and '--' for bullet points.
    - At the end, provide a section titled "Actionable Steps" summarizing key tasks.

    Important:
    - Include weather information only if a location is detected/needed for the desired task planning.
    - Make all steps actionable and clear for the user to follow.
    """

    plan = call_llm(prompt)

    # Replace default headings with emoji versions
    plan = plan.replace("Morning", "☀️ Morning")
    plan = plan.replace("Afternoon", "🌞 Afternoon")
    plan = plan.replace("Evening", "🌙 Evening")

    # Fallback if LLM returns empty
    if not plan.strip():
        plan = "Sorry, the plan could not be generated. Please try again."

    return plan


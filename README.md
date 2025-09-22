# 🗺️ AI Task & Trip Planner

An AI-powered agent that helps you turn natural language goals into **structured, actionable plans**.  
It combines an LLM with web search + weather APIs, stores results in a database, and gives you a simple web interface.

---

## 🚀 How it Works

### Workflow
1. **Input**: User enters a goal (e.g., *"Plan a 2-day vegetarian food tour in Hyderabad"*).
2. **Planner**:  
   - LLM breaks it down into actionable steps.  
   - **Tavily API** enriches with web results.  
   - **OpenWeather API** adds weather context if location is detected.  
3. **Storage**: Goal + plan saved in SQLite database.  
4. **UI**: Streamlit web app to view current + past plans.

---

### Architecture Diagram

```text
         ┌──────────────┐
         │   User Goal  │
         └──────┬───────┘
                │
        ┌───────▼────────┐
        │    Planner     │
        │  (LLM + tools) │
        └───────┬────────┘
    ┌───────────┴───────────┐
    │  Web Search (Tavily)  │
    │  Weather (OpenWeather)│
    └───────────┬───────────┘
                │
        ┌───────▼────────┐
        │    Database    │
        │    (SQLite)    │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │   Streamlit UI │
        └────────────────┘

## ⚙️ Setup & Run

1. Clone Repo

git clone https://github.com/yourusername/ai-task-planner.git
cd ai-task-planner

2. Install Dependencies

pip install -r requirements.txt

3. Add Environment Variables

Create a .env file in project root:

OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
OPENWEATHER_API_KEY=your_openweather_key

4. Run App

streamlit run app.py
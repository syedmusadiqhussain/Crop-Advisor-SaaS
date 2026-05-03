
---

# 🌾 Crop Advisor — Precision Agriculture SaaS

Deliver weather‑aware, localized crop recommendations powered by OpenRouter (OpenAI-compatible API) with free-model support. Fast Streamlit UI, actionable insights, and a configurable AI sidebar that adapts to your usage.

---

## ✨ Key Features

- ⚡ AI Model Selection: Uses OpenRouter models (including free tiers) with a sidebar selector to switch models when needed
- 📍 Localized Recommendations: Enter your crop and city to get tailored guidance based on current and forecasted conditions
- 🛠️ Advanced Configuration Sidebar: Reset conversation, change models, and manage session state without leaving the page
- 🌤️ Weather Dashboard: Bento‑style grid highlighting temperature, humidity, wind, pressure, and forecast indicators
- 💬 Conversational Assistant: Follow‑up Q&A with memory for context‑aware recommendations

---

## 🧱 Tech Stack

- Streamlit (UI and app framework)
- OpenRouter (OpenAI-compatible) via LangChain ChatOpenAI
- Python (3.10+ recommended)
- OpenWeatherMap API (current weather and 24h forecast)

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/syedmusadiqhussain/Crop-Advisor-SaaS.git
cd Crop-Advisor-SaaS
```

Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Setup

Create a `.env` file in the project root and add:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
WEATHER_API_KEY=your_openweathermap_api_key
```

Notes:
- The `.gitignore` already excludes `.env` for safety
- If you just generated your OpenWeatherMap key, activation can take up to 2 hours
- For Hugging Face Spaces, set the same values in Space Settings → Secrets (recommended). The app reads from `st.secrets` first and falls back to environment variables for local dev.

---

## 🚀 Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Using the app:
- Enter your Crop Name (e.g., “Organic Wheat”) and Location (e.g., “Islamabad”)
- Click “Generate Recommendation” to produce an initial, weather‑aware strategy
- Review the Weather Dashboard on the left
- Use the right‑side chat (“Crop Intelligence”) for follow‑up questions (irrigation, pests, harvesting, etc.)
- Switch AI models or reset the conversation via the sidebar if you hit rate limits

---

## 🗺️ Roadmap

- Real‑time weather improvements (alerts, severe weather advisories)
- Soil sensor data ingestion for hyper‑local recommendations
- Multi‑language support for regional deployment
- Export to PDF/CSV for farm reports
- Offline/low‑connectivity mode with cached recommendations

---

## 🤝 Contributing

Pull requests and feature suggestions are welcome. Please open an issue to discuss major changes.

---

## 📜 License

MIT License

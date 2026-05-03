import streamlit as st
import os
import requests
import warnings
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🌾 Crop Advisor", layout="wide")

# =========================
# PREMIUM CSS STYLING
# =========================
def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;600;700&display=swap');

        /* Global Overrides */
        :root {
            --bg-deep: #0E1117;
            --emerald: #10B981;
            --gold: #F59E0B;
            --glass-bg: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-main: #E5E7EB;
            --text-dim: #9CA3AF;
        }

        .stApp {
            background-color: var(--bg-deep);
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        /* Glassmorphism Card */
        .glass-card {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: fadeIn 0.8s ease-out;
        }

        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            border-color: rgba(16, 185, 129, 0.3);
        }

        /* Bento Grid */
        .bento-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 16px;
            margin: 20px 0;
        }

        .bento-item {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }

        .bento-item:hover {
            background: rgba(16, 185, 129, 0.1);
            border-color: var(--emerald);
            transform: scale(1.02);
        }

        .bento-icon {
            font-size: 24px;
            margin-bottom: 8px;
            display: block;
        }

        .bento-label {
            font-size: 12px;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .bento-value {
            font-size: 18px;
            font-weight: 700;
            color: var(--gold);
            margin-top: 4px;
        }

        /* Premium Chat Interface */
        .chat-container {
            max-height: 600px;
            overflow-y: auto;
            padding-right: 10px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .chat-bubble {
            max-width: 85%;
            padding: 14px 18px;
            border-radius: 18px;
            font-size: 14.5px;
            line-height: 1.5;
            position: relative;
            animation: slideIn 0.4s ease-out;
        }

        .chat-bubble-user {
            align-self: flex-end;
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .chat-bubble-ai {
            align-self: flex-start;
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            color: white;
            border-bottom-left-radius: 4px;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }

        .ai-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
            font-weight: 600;
            font-size: 12px;
            color: rgba(255,255,255,0.9);
        }

        .sparkle-icon {
            animation: sparkle 1.5s infinite ease-in-out;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0B0E14;
            border-right: 1px solid var(--glass-border);
        }

        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stButton button {
            font-family: 'Poppins', sans-serif;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        @keyframes sparkle {
            0%, 100% { opacity: 0.6; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }

        /* Customizing Streamlit Inputs */
        .stTextInput input {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid var(--glass-border) !important;
            color: white !important;
            border-radius: 10px !important;
        }

        .stButton button {
            background: linear-gradient(90deg, var(--emerald) 0%, #059669 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            transition: all 0.3s ease !important;
        }

        .stButton button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.4) !important;
        }

        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)


# =========================
# INITIAL SETUP
# =========================
def get_secret_or_env(key: str):
    try:
        secrets = st.secrets
        if key in secrets:
            value = secrets.get(key)
            if value:
                return value
    except Exception:
        pass
    value = os.getenv(key)
    return value if value else None


def load_env_vars():
    load_dotenv()
    weather_api_key = get_secret_or_env("WEATHER_API_KEY")
    openrouter_api_key = get_secret_or_env("OPENROUTER_API_KEY") or get_secret_or_env("OPENAI_API_KEY")
    demo_mode = os.getenv("DEMO_MODE", "").strip().lower() in {"1", "true", "yes", "on"}
    return weather_api_key, openrouter_api_key, demo_mode


class DemoConversation:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def invoke(self, query: str):
        return (
            "Demo mode is enabled, so this is a sample recommendation.\n\n"
            "- Use well-drained soil and maintain consistent moisture.\n"
            "- Water early morning; reduce irrigation when humidity is high.\n"
            "- Increase scouting for pests after rain or warm nights.\n"
            "- Mulch to reduce evaporation and stabilize soil temperature.\n"
            "- Use windbreaks or staking if strong winds are expected."
        )


class OpenRouterConversation:
    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float = 0.3,
        max_output_tokens: int = 600,
    ):
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=max_output_tokens,
        )

    def invoke(self, query: str):
        return self.llm.invoke(query)


def init_llm_conversation(
    openrouter_api_key: str, model_name: str, demo_mode: bool = False
):
    if demo_mode:
        return DemoConversation(model_name=model_name)

    if not openrouter_api_key:
        st.warning("Please set OPENROUTER_API_KEY (or OPENAI_API_KEY) in the environment variables.")
        return None

    warnings.filterwarnings("ignore")
    return OpenRouterConversation(api_key=openrouter_api_key, model_name=model_name)


def call_conversation(conversation_obj, query: str) -> str:
    """Compatibility helper that always uses .invoke() and returns a string."""
    if conversation_obj is None:
        return "❌ **Error:** AI client is not configured. Set `OPENROUTER_API_KEY` (or enable `DEMO_MODE=1`)."
    try:
        result = conversation_obj.invoke(query)
        if isinstance(result, str):
            return result
        if isinstance(result, dict):
            return str(result.get("response") or result.get("content") or "")
        content = getattr(result, "content", None)
        if isinstance(content, str):
            return content
        return str(result)
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            return "⚠️ **Rate Limit Reached:** Please wait and retry, or switch the model in the sidebar."
        if "401" in error_str or "Unauthorized" in error_str:
            return "❌ **Unauthorized:** Check your `OPENROUTER_API_KEY`."
        return f"❌ **Error:** {error_str}"


# =========================
# WEATHER HELPERS
# =========================
def filter_data(data):
    unique_dates = set()
    filtered_data = []
    for entry in data["list"]:
        date = entry["dt_txt"][:-9]
        if date not in unique_dates:
            unique_dates.add(date)
            filtered_data.append(entry)
    return filtered_data


def check_weather_forecast(city, api_key):
    ndays = 40
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&cnt={ndays}&appid={api_key}"
    response = requests.get(url)
    if response.status_code != 200 or response.json().get("cod") == "404":
        return None, "City not found"

    data = response.json()
    filtered_data = filter_data(data)

    rain_threshold = 1.6
    wind_threshold = 20
    high_temp = 35
    low_temp = 0

    worst_days = []
    for day in filtered_data:
        date = day["dt_txt"]
        rain = day.get("rain", {}).get("3h", 0)
        wind = day["wind"]["speed"]
        temp_c = day["main"]["temp"] - 273.15

        if (
            rain >= rain_threshold
            or wind >= wind_threshold
            or temp_c >= high_temp
            or temp_c <= low_temp
        ):
            worst_days.append(date)

    return worst_days, None


# =========================
# MAIN APP LAYOUT
# =========================
def main():
    apply_custom_css()
    
    st.markdown("""
        <div style="text-align: center; padding: 20px 0; animation: fadeIn 1s ease-out;">
            <h1 style="font-family: 'Poppins', sans-serif; font-weight: 700; color: #10B981; margin-bottom: 0;">
                🌦️ Crop Advisor <span style="color: #F59E0B; font-weight: 300;">SaaS</span>
            </h1>
            <p style="color: #9CA3AF; font-size: 1.1rem; margin-top: 5px;">Precision Agriculture powered by OpenRouter</p>
        </div>
    """, unsafe_allow_html=True)

    weather_api_key, openrouter_api_key, demo_mode = load_env_vars()
    st.session_state.demo_mode = demo_mode

    # Sidebar for Settings
    with st.sidebar:
        st.markdown("<h2 style='font-family:Poppins; color:#10B981;'>⚙️ Configuration</h2>", unsafe_allow_html=True)
        
        with st.expander("🤖 Model Settings", expanded=True):
            selected_model = st.selectbox(
                "AI Intelligence Level",
                [
                    "google/gemini-2.0-flash-lite-001:free",
                    "mistralai/mistral-7b-instruct",
                    "mistralai/mistral-7b-instruct-v0.3",
                    "meta-llama/llama-3.1-8b-instruct",
                    "openai/gpt-4o-mini",
                ],
                help="Switch models if you hit rate limits."
            )
        
        with st.expander("🛠️ Advanced", expanded=False):
            if st.button("Clear Cache & History", use_container_width=True):
                st.session_state.conversation = init_llm_conversation(
                    openrouter_api_key, selected_model, demo_mode=st.session_state.get("demo_mode", False)
                )
                st.session_state.chat_history = []
                st.session_state.initial_reco_done = False
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
            <div style='padding: 10px; border-radius: 10px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2);'>
                <p style='color: #10B981; font-size: 0.8rem; margin: 0;'>
                    💡 <b>Tip:</b> Provide detailed crop varieties for better accuracy.
                </p>
            </div>
        """, unsafe_allow_html=True)

    if "conversation" not in st.session_state or st.session_state.get("current_model") != selected_model:
        st.session_state.conversation = init_llm_conversation(
            openrouter_api_key, selected_model, demo_mode=st.session_state.get("demo_mode", False)
        )
        st.session_state.current_model = selected_model
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        st.session_state.initial_reco_done = False
        st.session_state.weather_data = None
        st.session_state.current_city = None
        st.session_state.current_crop = None

    # Two-column layout
    col1, col2 = st.columns([1, 1])

    # -------- LEFT COLUMN: Inputs --------
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #10B981; margin-top:0;'>🧩 Parameters</h3>", unsafe_allow_html=True)
        crop = st.text_input("Crop Name", placeholder="e.g. Organic Wheat")
        city = st.text_input("Location", placeholder="e.g. Islamabad")
        get_reco = st.button("Generate Recommendation", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display weather data if available
        if st.session_state.weather_data:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #10B981; margin-top:0;'>🌤️ Weather Dashboard</h3>", unsafe_allow_html=True)
            
            w = st.session_state.weather_data
            st.markdown(f"""
                <div class='bento-grid'>
                    <div class='bento-item'>
                        <span class='bento-icon'>🌡️</span>
                        <span class='bento-label'>Temp</span>
                        <div class='bento-value'>{w['temp_c']}°C</div>
                    </div>
                    <div class='bento-item'>
                        <span class='bento-icon'>💧</span>
                        <span class='bento-label'>Humidity</span>
                        <div class='bento-value'>{w['humidity']}%</div>
                    </div>
                    <div class='bento-item'>
                        <span class='bento-icon'>🌬️</span>
                        <span class='bento-label'>Wind</span>
                        <div class='bento-value'>{w['wind_speed']}m/s</div>
                    </div>
                    <div class='bento-item'>
                        <span class='bento-icon'>📊</span>
                        <span class='bento-label'>Pressure</span>
                        <div class='bento-value'>{w['pressure']}hPa</div>
                    </div>
                </div>
                <div style='padding: 10px; border-radius: 8px; background: rgba(245, 158, 11, 0.1); border-left: 4px solid #F59E0B;'>
                    <p style='margin:0; color: #F59E0B; font-weight: 500;'>
                        <b>Condition:</b> {w['condition']} — {w['description'].title()}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            if w.get('forecast_avg_temp') != 'N/A':
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='font-size: 0.85rem; color: #9CA3AF; display: flex; justify-content: space-between;'>
                        <span>📈 24h Forecast Avg: <b>{w['forecast_avg_temp']}°C</b></span>
                        <span>☔ Rain: <b>{w['forecast_rain']}mm</b></span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if get_reco:
            if not weather_api_key and not demo_mode:
                st.error("Please set your Weather API key in .env file.")
                return

            if not crop or not city:
                st.warning("Please fill in both crop name and city.")
                return

            if demo_mode and not weather_api_key:
                weather_condition = "Clear"
                weather_description = "clear sky"
                temp_celsius = 26
                temp_fahrenheit = round(temp_celsius * 9 / 5 + 32)
                feels_like_c = 27
                humidity = 55
                pressure = 1012
                wind_speed = 3.2
                wind_direction = 120
                visibility = 10000
                uv_index = "N/A"
                avg_temp = 27
                avg_humidity = 52
                total_rain = 0.2
            else:
                response = requests.get(
                    f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID={weather_api_key}"
                )
                weather_data = response.json()

                if response.status_code != 200:
                    error_msg = weather_data.get("message", "Unknown error occurred")
                    if response.status_code == 401:
                        st.error(
                            f"Invalid Weather API Key: {error_msg}. If you just created the key, it may take up to 2 hours to activate."
                        )
                    elif response.status_code == 404:
                        st.error(f"City not found: {city}")
                    else:
                        st.error(f"Weather API Error ({response.status_code}): {error_msg}")
                    return

                weather_condition = weather_data["weather"][0]["main"]
                weather_description = weather_data["weather"][0]["description"]
                temp_celsius = round(weather_data["main"]["temp"])
                temp_fahrenheit = round(temp_celsius * 9 / 5 + 32)
                feels_like_c = round(weather_data["main"]["feels_like"])
                humidity = weather_data["main"]["humidity"]
                pressure = weather_data["main"]["pressure"]
                wind_speed = weather_data["wind"]["speed"]
                wind_direction = weather_data["wind"].get("deg", "N/A")
                visibility = weather_data.get("visibility", "N/A")
                uv_index = weather_data.get("uv", "N/A")

                forecast_response = requests.get(
                    f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&APPID={weather_api_key}"
                )
                forecast_data = forecast_response.json()

                avg_temp = "N/A"
                avg_humidity = "N/A"
                total_rain = "N/A"

                if forecast_response.status_code == 200:
                    forecast_list = forecast_data["list"][:8]
                    avg_temp = round(sum(item["main"]["temp"] for item in forecast_list) / len(forecast_list))
                    avg_humidity = round(
                        sum(item["main"]["humidity"] for item in forecast_list) / len(forecast_list)
                    )
                    total_rain = sum(item.get("rain", {}).get("3h", 0) for item in forecast_list)
                else:
                    st.warning(f"Could not fetch forecast data: {forecast_data.get('message', 'Unknown error')}")
            
            # Store weather data in session state
            st.session_state.weather_data = {
                'condition': weather_condition,
                'description': weather_description,
                'temp_c': temp_celsius,
                'temp_f': temp_fahrenheit,
                'feels_like': feels_like_c,
                'humidity': humidity,
                'pressure': pressure,
                'wind_speed': wind_speed,
                'wind_direction': wind_direction,
                'visibility': visibility,
                'uv_index': uv_index,
                'forecast_avg_temp': avg_temp,
                'forecast_avg_humidity': avg_humidity,
                'forecast_rain': total_rain
            }
            st.session_state.current_city = city
            st.session_state.current_crop = crop

            if demo_mode and not weather_api_key:
                worst_days, error = [], None
            else:
                worst_days, error = check_weather_forecast(city, weather_api_key)

            if error:
                st.error(error)
            else:
                st.write("🌧️ **Worst Weather Days:**")
                if worst_days:
                    for d in worst_days:
                        st.write(f"- {d}")
                else:
                    st.write("No severe weather in forecast.")

            # Create comprehensive prompt for crop recommendations
            query = f"""
            As an expert agricultural advisor, please provide brief recommendations for growing {crop} in {city}. Consider the following current conditions and factors:

            CURRENT WEATHER CONDITIONS:
            - Weather: {weather_condition} ({weather_description})
            - Temperature: {temp_celsius}°C ({temp_fahrenheit}°F), Feels like: {feels_like_c}°C
            - Humidity: {humidity}%
            - Atmospheric Pressure: {pressure} hPa
            - Wind Speed: {wind_speed} m/s, Direction: {wind_direction}°
            - Visibility: {visibility}m
            - UV Index: {uv_index}

            FORECAST TRENDS (24h):
            - Average Temperature: {round(avg_temp) if 'avg_temp' in locals() else 'N/A'}°C
            - Average Humidity: {round(avg_humidity) if 'avg_humidity' in locals() else 'N/A'}%
            - Expected Rainfall: {total_rain if 'total_rain' in locals() else 'N/A'}mm

            Please provide recommendations briefly considering:
            1. Optimal growing conditions for {crop}
            2. Current weather suitability and potential risks
            3. Seasonal timing and planting windows
            4. Soil preparation and irrigation needs
            5. Pest and disease management based on weather conditions
            6. Harvest timing considerations
            7. Any weather-related precautions or protective measures
            8. Alternative crops if current conditions are unfavorable

            Provide specific, actionable advice tailored to the current conditions in {city}.
            Provide the answer in a concise manner.
            """
            with st.spinner("🤖 AI is analyzing weather data and generating recommendations..."):
                response = call_conversation(st.session_state.conversation, query)
                reply = response

            st.session_state.chat_history.append(("User", query))
            st.session_state.chat_history.append(("Assistant", reply))
            
            # Enhanced success message
            st.markdown("""
            <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); 
                        padding: 1rem; 
                        border-radius: 10px; 
                        text-align: center;
                        margin: 1rem 0;">
                <p style="color: #2d5016; margin: 0; font-weight: 600; font-size: 1rem;">
                    ✅ Recommendation added to chatbot panel →
                </p>
            </div>
            """, unsafe_allow_html=True)
            # Mark that initial recommendation has been generated so chat input is enabled
            st.session_state.initial_reco_done = True
            # Rerun so the UI updates and enables the chat input
            st.rerun()

    # -------- RIGHT COLUMN: Chatbot --------
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #10B981; margin-top:0;'>💬 Crop Intelligence</h3>", unsafe_allow_html=True)

        # Chat messages container
        if st.session_state.chat_history:
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
            for speaker, message in st.session_state.chat_history:
                if speaker == "User":
                    # Extract first line for display
                    first_line = message.split('\n')[0].strip()
                    if "Growing" in first_line and "growing" in first_line.lower():
                        first_line = f"Analyze conditions for {st.session_state.current_crop}"
                    
                    st.markdown(f"""
                        <div class='chat-bubble chat-bubble-user'>
                            {first_line}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class='chat-bubble chat-bubble-ai'>
                            <div class='ai-header'>
                                <span class='sparkle-icon'>✨</span> AI RECOMMENDATION
                            </div>
                            {message}
                        </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style='text-align: center; padding: 40px 20px;'>
                    <div style='font-size: 50px; margin-bottom: 20px;'>🤖</div>
                    <h4 style='color: #E5E7EB; margin-bottom: 10px;'>Ready for Analysis</h4>
                    <p style='color: #9CA3AF; font-size: 0.9rem;'>
                        Complete the parameters on the left to generate your first weather-aware crop strategy.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        if not st.session_state.get("initial_reco_done", False):
            st.chat_input("Chat is locked until recommendation is generated", disabled=True)
        else:
            follow_up = st.chat_input("Ask about irrigation, pests, or harvesting...")

            if follow_up:
                st.session_state.chat_history.append(("User", follow_up))
                with st.spinner("🤖 Consulting AI Models..."):
                    reply = call_conversation(st.session_state.conversation, follow_up)
                    reply_text = reply
                st.session_state.chat_history.append(("Assistant", reply_text))
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

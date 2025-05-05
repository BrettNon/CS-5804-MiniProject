import streamlit as st
import requests
from datetime import datetime

# === CONFIG ===
API_KEY = "487b5fb53375ce05ec087ffe51ebc0d9"
DEFAULT_LAT = 37.2296
DEFAULT_LON = -80.4139

# === VT Styling ===
st.set_page_config(page_title="VT Weather Forecast", page_icon="🌦️")
st.markdown("""
<style>
/* Expand app to full width */
[data-testid="stAppViewContainer"] > .main {
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}

/* Tighter layout */
section[data-testid="stSidebar"] {
    width: 300px;
}

h1 {
    color: #861F41;
}

/* Input and buttons in VT colors */
.stTextInput > div > div > input {
    border: 2px solid #E5751F;
}
.stButton > button {
    background-color: #861F41;
    color: white;
    font-weight: bold;
}
.stButton > button:hover {
    background-color: #E5751F;
}
</style>
""", unsafe_allow_html=True)

st.title("🌦️ Virginia Tech 7-Day Weather Forecast")

# === Functions ===
def get_coordinates(city_name):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
    resp = requests.get(geo_url).json()
    if resp and len(resp) > 0:
        return resp[0]['lat'], resp[0]['lon']
    else:
        st.warning("City not found. Using default (Blacksburg, VA).")
        return DEFAULT_LAT, DEFAULT_LON

def fetch_7_day_forecast(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/forecast/daily"
    params = {
        "lat": lat,
        "lon": lon,
        "cnt": 7,
        "appid": API_KEY,
        "units": "metric"
    }
    return requests.get(url, params=params).json()

def summarize_forecast(forecast):
    summary = []
    for day_data in forecast["list"]:
        date = datetime.utcfromtimestamp(day_data["dt"]).strftime('%A, %b %d')
        temp = day_data["temp"]["day"]
        desc = day_data["weather"][0]["description"].title()
        summary.append(f"{date}: {temp}°C, {desc}")
    return "\n".join(summary)

def query_llm_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        return response.json().get("response", "No response.")
    except Exception as e:
        return f"LLM error: {e}"

# === City Selection ===
city = st.text_input("Enter a city name (optional):", value="Blacksburg, VA")
lat, lon = get_coordinates(city)

# === Layout: 2 Columns (Forecast | Chatbot) ===
left_col, right_col = st.columns(2)

# === Left: Forecast ===
with left_col:
    st.subheader("📅 7-Day Forecast")
    with st.spinner("Loading forecast..."):
        forecast = fetch_7_day_forecast(lat, lon)

        if "list" in forecast:
            summary = summarize_forecast(forecast)
            st.text(summary)
        else:
            st.error("Could not fetch forecast data.")
            summary = ""

# === Right: Chatbot ===
with right_col:
    st.subheader("💬 Ask about the forecast")

    if summary:
        user_question = st.text_input("Ask a question about the weather:")
        if user_question:
            prompt = f"The following is a 7-day weather forecast:\n{summary}\n\nQuestion: {user_question}\nAnswer:"
            with st.spinner("Thinking..."):
                reply = query_llm_ollama(prompt)
            st.success(reply)


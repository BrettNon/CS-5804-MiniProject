import streamlit as st
import requests
from datetime import date, datetime
import pandas as pd

import model_query

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
        st.warning("City not found. Using default (Blacksburg, Virginia).")
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
            timeout=120
        )
        return response.json().get("response", "No response.")
    except Exception as e:
        return f"LLM error: {e}"
    
station_to_city = {
    'New Market Airport': 'New Market', 
     'Norfolk / Granby Shores': 'Norfolk', 
     'Norfolk International Airport': 'Norfolk', 
     'Richmond International  Airport': 'Richmond', 
     'Wallops Flight Fac Airport': 'Wallops Island', 
     'Dulles International Airport': 'Dulles', 
     'Lynchburg Regional Airport': 'Lynchburg', 
     'Roanoke Regional Airport': 'Roanoke', 
     'Langley Air Force Base': 'Hampton', 
     'Jonesville / Cedar Hill': 'Jonesville', 
     'Wakefield': 'Wakefield', 
     'South Hill / Brodnax': 'South Hill', 
     'Blacksburg / Airport Acres': 'Blacksburg', 
     'Ft Pickett / Blackstone': 'Blackstone', 
     'Charlottesville / Deerwood': 'Charlottesville', 
     'Culpeper / Elkwood': 'Culpeper', 
     'Norfolk / Cornland': 'Norfolk', 
     'Chase City / Spanish Grove': 'Chase City', 
     'Danville / Green Acres': 'Danville', 
     'Emporia / James River Junction': 'Emporia', 
     'Shannon / Sylvania Heights': 'Shannon', 
     'Fort Eustis / Hoopes Landing': 'Fort Eustis', 
     'Richmond / Robinwood': 'Richmond', 
     'Franklin / Lees Mill': 'Franklin', 
     'Front Royal / Mineral Springs': 'Front Royal', 
     'Farmville / Reeds': 'Farmville', 
     'West Point / Brookeshire': 'West Point', 
     'Gordonsville': 'Gordonsville', 
     'Manassas / Bristow': 'Manassas', 
     'Hillsville / Five Forks': 'Hillsville', 
     'Hot Springs / Healing Springs': 'Bath County', 
     'Warrenton / Midland': 'Warrenton', 
     'Richlands / Birmingham': 'Richlands', 
     'Williamsburg / Kingspoint': 'Williamsburg', 
     'Leesburg / Sycolin': 'Leesburg', 
     'Louisa': 'Louisa', 
     'Wise / Hurricane': 'Wise', 
     'Luray / Westlu': 'Luray', 
     'Lawrenceville / Edgerton': 'Lawrenceville', 
     'Melfa': 'Melfa', 
     'Marion / Groseclose': 'Marion', 
     'Martinsville B Ridge Airport / Old Well Crossing': 'Martinsville', 
     'Fentress / Mount Pleasant': 'Fentress', 
     'Virginia Beach / Gatewood Park': 'Virginia Beach', 
     'Quantico': 'Quantico', 
     'Richmond / Brown Grove': 'Richmond', 
     'Winchester / Bufflick Heights': 'Winchester', 
     'Orange / Nasons': 'Orange', 
     'Newport News Airport': 'Newport News', 
     'Dublin / Highland Park': 'Dublin', 
     'Petersburg / Jack': 'Petersburg', 
     'Norfolk / Algren': 'Norfolk', 
     'Stafford / Ramoth Church Estates': 'Stafford', 
     'Suffolk / Russell': 'Suffolk', 
     'Staunton / Weyers Cave': 'Staunton', 
     'Tangier Island': 'Tangier Island', 
     'Bridgewater / Mount Crawford': 'Bridgewater', 
     'Abington / Rust Hollow': 'Abington', 
     'Waynesboro / Claymont Manor': 'Waynesboro', 
     'Kenbridge / Plymouth': 'Kenbridge', 
     'Clarksville / Blanks': 'Clarksville', 
     'Saluda / Locklies': 'Saluda', 
     'South Boston / Five Forks': 'South Boston', 
     'Crewe': 'Crewe', 
     'Quinton / Wrights Corner': 'Quinton', 
     'Tappahannock / Pauls Crossroads': 'Tappahannock', 
     'Fort Belvoir': 'Fort Belvoir', 
     'Lake Anna Airport': 'Bumpass', 
     'Campbell County Airport': 'Gladys',
}

# === City Selection ===
df = pd.read_csv('virginia_all_stations_weather.csv')
stations = df['station_name'].unique().tolist()
selected_station = st.selectbox("Choose a City / Weather Station", ["Custom"]+ stations)

if selected_station == "Custom":
    city = st.text_input("Enter a city name (optional):", value="Blacksburg, Virginia")
    lat, lon = get_coordinates(city)
else:
    city = station_to_city[selected_station]
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
            if selected_station == "Custom":
                prompt = f"Today is {date.today()}\n\nThe following is a 7-day weather forecast:\n{summary}\n\nQuestion: {user_question}\nAnswer:"
                with st.spinner("Thinking..."):
                    reply = query_llm_ollama(prompt)
                st.success(reply)
            else:
                prompt = f"Today is {date.today()}\n\nThe following is a 7-day weather forecast:\n{summary}\n\n{model_query.generate_forecast(selected_station, date.today(), 30)}\n\nQuestion: {user_question}\nAnswer:"
                with st.spinner("Thinking..."):
                    reply = query_llm_ollama(prompt)
                st.success(reply)


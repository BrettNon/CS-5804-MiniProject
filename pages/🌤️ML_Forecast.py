import re
import streamlit as st
import joblib
import pandas as pd
from datetime import date, timedelta
import numpy as np
import altair as alt

# Load data
df = pd.read_csv('virginia_all_stations_weather.csv')
stations = df['station_name'].unique().tolist()

# Celsius to Fahrenheit conversion
def c_to_f(c): return (c * 9/5) + 32

# Degrees to cardinal direction conversion
def degrees_to_cardinal(degrees):
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    idx = int((degrees % 360) / 45 + 0.5) % 8
    return directions[idx]

# Streamlit app
st.set_page_config(page_title="Virginia ML Weather Forecast", page_icon="🌤️")
st.title("🌤️ 7-Day Virginia ML Weather Forecast")

# Allow user to select a city / weather station and start date
selected_station = st.selectbox("Choose a City / Weather Station", stations)
start_date = st.date_input("Start Date", date.today())

safe_station = re.sub(r'[^\w\-_.]', '_', selected_station)
model = joblib.load(f"models/model_{safe_station}.joblib")

if st.button("Generate Forecast"):
    dates = [start_date + timedelta(days=i) for i in range(7)]
    features = pd.DataFrame({
        'dayofyear': [d.timetuple().tm_yday for d in dates],
        'month': [d.month for d in dates],
        'year': [d.year for d in dates]
    })

    preds = model.predict(features)
    df_pred = pd.DataFrame(preds, columns=['tavg', 'tmin', 'tmax', 'prcp', 'wdir', 'wspd'])
    df_pred['Date'] = dates

    # Convert temperature columns to Fahrenheit
    for col in ['tavg', 'tmin', 'tmax']:
        df_pred[col] = df_pred[col].apply(c_to_f)

    # Reorder columns
    df_pred = df_pred[['Date', 'tavg', 'tmin', 'tmax', 'prcp', 'wspd', 'wdir']]
    df_pred = df_pred.round(2)
    df_pred = df_pred.rename(columns={
    'tavg': 'Average Temp (°F)',
    'tmin': 'Min Temp (°F)',
    'tmax': 'Max Temp (°F)',
    'prcp': 'Precipitation (inches)',
    'wspd': 'Wind Speed (mph)',
    'wdir': 'Wind Direction'
    })

    df_pred['Wind Direction'] = df_pred['Wind Direction'].apply(degrees_to_cardinal)

    # Display the forecast table
    st.subheader("📋 Forecast Table (7 Days)")
    st.dataframe(df_pred.set_index("Date"), use_container_width=True)

    # Prepare data for Altair chart
    temp_df = df_pred.melt(
        id_vars=['Date'],
        value_vars=['Max Temp (°F)' ,'Average Temp (°F)', 'Min Temp (°F)'],
        var_name='Temperature Type',
        value_name='Temperature (°F)'
    )

    # Create Altair chart for Temperature
    temp_chart = alt.Chart(temp_df).mark_line(strokeWidth=5).encode(
        x='Date:T',
        y='Temperature (°F):Q',
        color='Temperature Type:N'
    ).properties(
        title="Temperature Forecast (Min / Avg / Max)"
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_legend(
        titleFontSize=14,
        labelFontSize=12
    ).configure_title(
        fontSize=16
    )

    # Create Altair chart for Precipitation
    precip_chart = alt.Chart(df_pred).mark_bar().encode(
        x='Date:T',
        y='Precipitation (inches):Q'
    ).properties(
        title="Precipitation"
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16
    )

    # Create Altair chart for Wind Speed
    wind_chart = alt.Chart(df_pred).mark_line(strokeWidth=5).encode(
        x='Date:T',
        y='Wind Speed (mph):Q'
    ).properties(
        title="Wind Speed Forecast"
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16
    )

    # Display the charts
    st.markdown("### 📈 Temperature Forecast")
    st.altair_chart(temp_chart, use_container_width=True)

    st.markdown("### 🌧️ Precipitation")
    st.altair_chart(precip_chart, use_container_width=True)

    st.markdown("### 💨 Wind Speed")
    st.altair_chart(wind_chart, use_container_width=True)

import re
import joblib
import pandas as pd
from datetime import date, timedelta

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


def generate_forecast(selected_station, start_date = date.today(), day_cnt = 7):
    safe_station = re.sub(r'[^\w\-_.]', '_', selected_station)
    model = joblib.load(f"models/model_{safe_station}.joblib")

    dates = [start_date + timedelta(days=i) for i in range(day_cnt)]
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

    df_pred['wdir'] = df_pred['wdir'].apply(degrees_to_cardinal)

    summary = []
    for day_data in df_pred.iterrows():
        date = day_data[1]['Date'].strftime('%A, %b %d')
        avg_temp = day_data[1]['tavg']
        min_temp = day_data[1]['tmin']
        max_temp = day_data[1]['tmax']
        precip = day_data[1]['prcp']
        wind_speed = day_data[1]['wspd']
        wind_dir = day_data[1]['wdir']
        summary.append(f"{date}: {avg_temp}°F, {min_temp}°F, {max_temp}°F, {precip} inches, {wind_speed} mph, {wind_dir}")

    summary = "\n".join(summary)
    prompt = f"The following is a detailed weather forecast in the format of 'Date: Average Temp(°F), Min Temp(°F), Max Temp(°F), Precipitation(inches), Wind Speed(mph),  Wind Direction:\n{summary}\n\n"
    return prompt


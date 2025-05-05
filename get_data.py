from meteostat import Stations, Daily
from datetime import datetime
import pandas as pd
import time

# Set date range for historical weather data
start = datetime(2010, 1, 1)
end = datetime(2025, 1, 1)

# Fetch all stations in Virginia
stations = Stations().region('US', 'VA').fetch()

# Store all station data
all_data = []

# Loop through stations
for station_id, row in stations.iterrows():
    name = row['name']
    print(f"📥 Fetching data for: {name} (ID: {station_id})")

    try:
        data = Daily(station_id, start, end).fetch()
        data = data.reset_index()
        data['station_id'] = station_id
        data['station_name'] = name
        all_data.append(data)
    except Exception as e:
        print(f"⚠️ Error fetching {name}: {e}")
    
    time.sleep(1)

# Combine and save
if all_data:
    combined = pd.concat(all_data, ignore_index=True)
    combined.to_csv('virginia_all_stations_weather.csv', index=False)
    print("✅ Saved to virginia_all_stations_weather.csv")
else:
    print("❌ No data retrieved.")
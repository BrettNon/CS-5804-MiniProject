import requests

# Replace with your actual API key
API_KEY = "487b5fb53375ce05ec087ffe51ebc0d9"

# Sample coordinates (latitude/longitude) and request
url = "https://api.openweathermap.org/data/2.5/forecast/daily"
params = {
    "lat": 44.34,
    "lon": 10.99,
    "cnt": 7,
    "appid": API_KEY,
    "units": "metric"
}

response = requests.get(url, params=params)

print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(response.json())

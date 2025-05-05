import os
import re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

# Load data
df = pd.read_csv('virginia_all_stations_weather.csv', parse_dates=['time'])
df = df.set_index('time')

# Drop unnecessary columns
df = df.drop(columns=['snow', 'wpgt','tsun', 'pres', 'station_id'])

# Drop rows with NaN values in the target columns
df = df.dropna(subset=['tavg', 'tmin', 'tmax', 'prcp', 'wdir', 'wspd'])

# Feature engineering: date features
df['dayofyear'] = df.index.dayofyear
df['month'] = df.index.month
df['year'] = df.index.year

# Group by station and train a model for each
for station, group in df.groupby('station_name'):
    # Prepare features and targets
    X = group[['dayofyear', 'month', 'year']]
    y = group[['tavg', 'tmin', 'tmax', 'prcp', 'wdir', 'wspd']]

    # Skip small datasets
    if len(group) < 100:
        print(f"❌ Skipping {station} (not enough data: {len(group)} rows)")
        continue

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"✅ {station} - MAE: {mae:.2f}")

    # Save model with station name in filename (safe format)
    safe_station = re.sub(r'[^\w\-_.]', '_', station)
    filename = f"models/model_{safe_station}.joblib"
    joblib.dump(model, filename)
    print(f"✅ Saved model to {filename}")
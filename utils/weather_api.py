import os
import requests
import json
from datetime import datetime, timedelta
import random

# In a production environment, we would use a real weather API like OpenWeatherMap, Weather.com, etc.
# For this demonstration, we'll implement a mock API that returns realistic but simulated data

def get_api_key():
    """
    Get the API key for the weather service from environment variables
    
    Returns:
        API key string
    """
    # In production, this would use an actual API key from environment variables
    return os.getenv("WEATHER_API_KEY", "")

def get_current_weather(location=None):
    """
    Get current weather conditions for the specified location
    
    Args:
        location: Location string (city, coordinates, etc.)
        
    Returns:
        Dictionary with current weather data
    """
    api_key = get_api_key()
    
    # In production, we would make an actual API call like this:
    # if api_key and location:
    #     url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         return response.json()
    
    # Since we don't have an actual API key, we'll return simulated data
    current_date = datetime.now()
    
    # Generate realistic weather data based on current date
    # This is just for demonstration purposes
    month = current_date.month
    
    # Seasonal temperature and precipitation variations
    if 3 <= month <= 5:  # Spring
        temp = random.uniform(15, 25)
        humidity = random.uniform(50, 70)
        wind_speed = random.uniform(5, 15)
        precipitation = random.uniform(0, 5)
        condition = random.choice(["Partly Cloudy", "Sunny", "Light Rain"])
    elif 6 <= month <= 8:  # Summer
        temp = random.uniform(25, 35)
        humidity = random.uniform(40, 60)
        wind_speed = random.uniform(3, 10)
        precipitation = random.uniform(0, 2)
        condition = random.choice(["Sunny", "Clear", "Partly Cloudy"])
    elif 9 <= month <= 11:  # Fall
        temp = random.uniform(10, 20)
        humidity = random.uniform(60, 80)
        wind_speed = random.uniform(8, 18)
        precipitation = random.uniform(0, 10)
        condition = random.choice(["Cloudy", "Light Rain", "Partly Cloudy"])
    else:  # Winter
        temp = random.uniform(0, 10)
        humidity = random.uniform(70, 90)
        wind_speed = random.uniform(10, 20)
        precipitation = random.uniform(0, 15)
        condition = random.choice(["Cloudy", "Rain", "Snow"])
    
    # Small random change from yesterday
    temp_change = random.uniform(-2, 2)
    
    # Soil moisture estimate based on recent precipitation
    soil_moisture = min(100, max(30, 50 + precipitation * 3))
    
    # UV index based on season and cloud cover
    uv_index = 8 if condition == "Sunny" and 3 <= month <= 8 else random.randint(2, 5)
    
    # Compile current weather data
    weather_data = {
        "temp": round(temp, 1),
        "temp_change": round(temp_change, 1),
        "humidity": round(humidity, 1),
        "wind_speed": round(wind_speed, 1),
        "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
        "precipitation": round(precipitation, 1),
        "condition": condition,
        "pressure": round(random.uniform(990, 1020), 1),
        "visibility": round(random.uniform(8, 10), 1),
        "uv_index": uv_index,
        "soil_moisture": round(soil_moisture, 1),
        "updated": current_date.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return weather_data

def get_weather_forecast(location=None, days=7):
    """
    Get weather forecast for the specified location
    
    Args:
        location: Location string (city, coordinates, etc.)
        days: Number of days to forecast
        
    Returns:
        List of dictionaries with forecast data
    """
    api_key = get_api_key()
    
    # In production, we would make an actual API call like this:
    # if api_key and location:
    #     url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days}"
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         return process_forecast(response.json())
    
    # Since we don't have an actual API key, we'll return simulated data
    current_date = datetime.now()
    
    # Generate a realistic weather forecast
    forecast = []
    
    for i in range(days):
        forecast_date = current_date + timedelta(days=i)
        month = forecast_date.month
        
        # Base conditions on season with some randomness
        if 3 <= month <= 5:  # Spring
            temp_max = random.uniform(18, 28)
            temp_min = random.uniform(10, 15)
            precipitation = random.uniform(0, 15) if random.random() < 0.4 else 0
            condition = random.choice(["Partly Cloudy", "Sunny", "Light Rain", "Scattered Showers"])
        elif 6 <= month <= 8:  # Summer
            temp_max = random.uniform(28, 38)
            temp_min = random.uniform(18, 25)
            precipitation = random.uniform(0, 10) if random.random() < 0.3 else 0
            condition = random.choice(["Sunny", "Clear", "Partly Cloudy", "Isolated Thunderstorms"])
        elif 9 <= month <= 11:  # Fall
            temp_max = random.uniform(15, 25)
            temp_min = random.uniform(5, 15)
            precipitation = random.uniform(0, 20) if random.random() < 0.5 else 0
            condition = random.choice(["Cloudy", "Light Rain", "Partly Cloudy", "Showers"])
        else:  # Winter
            temp_max = random.uniform(5, 15)
            temp_min = random.uniform(-5, 5)
            precipitation = random.uniform(0, 25) if random.random() < 0.6 else 0
            condition = random.choice(["Cloudy", "Rain", "Snow", "Sleet"])
        
        # Add some continuity with previous day for realism
        if i > 0:
            prev_temp_max = forecast[i-1]['temp_max']
            prev_temp_min = forecast[i-1]['temp_min']
            prev_condition = forecast[i-1]['condition']
            
            # Smooth temperature changes
            temp_max = (temp_max + prev_temp_max) / 2
            temp_min = (temp_min + prev_temp_min) / 2
            
            # Weather conditions tend to persist
            if random.random() < 0.6:
                condition = prev_condition
        
        # Wind speed based on conditions
        if "Storm" in condition or "Rain" in condition:
            wind_speed = random.uniform(10, 25)
        else:
            wind_speed = random.uniform(5, 15)
        
        forecast.append({
            "date": forecast_date.strftime("%Y-%m-%d"),
            "temp_max": round(temp_max, 1),
            "temp_min": round(temp_min, 1),
            "precipitation": round(precipitation, 1),
            "humidity": round(random.uniform(60, 90), 1),
            "wind_speed": round(wind_speed, 1),
            "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "condition": condition
        })
    
    return forecast

def get_historical_weather(location=None, start_date=None, end_date=None):
    """
    Get historical weather data for the specified location and date range
    
    Args:
        location: Location string (city, coordinates, etc.)
        start_date: Start date string in format YYYY-MM-DD
        end_date: End date string in format YYYY-MM-DD
        
    Returns:
        List of dictionaries with historical weather data
    """
    api_key = get_api_key()
    
    # In production, we would make actual API calls to get historical data
    # For this demo, we'll generate simulated historical data
    
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    # Parse dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Calculate number of days
    days = (end - start).days + 1
    
    # Generate historical data
    historical_data = []
    
    for i in range(days):
        date = start + timedelta(days=i)
        month = date.month
        
        # Base conditions on season with some randomness
        if 3 <= month <= 5:  # Spring
            temp_max = random.uniform(15, 25)
            temp_min = random.uniform(5, 15)
            precipitation = random.uniform(0, 20) if random.random() < 0.4 else 0
        elif 6 <= month <= 8:  # Summer
            temp_max = random.uniform(25, 35)
            temp_min = random.uniform(15, 25)
            precipitation = random.uniform(0, 15) if random.random() < 0.3 else 0
        elif 9 <= month <= 11:  # Fall
            temp_max = random.uniform(10, 20)
            temp_min = random.uniform(0, 10)
            precipitation = random.uniform(0, 25) if random.random() < 0.5 else 0
        else:  # Winter
            temp_max = random.uniform(0, 10)
            temp_min = random.uniform(-10, 0)
            precipitation = random.uniform(0, 30) if random.random() < 0.6 else 0
        
        # Add some continuity with previous day for realism
        if i > 0:
            prev_temp_max = historical_data[i-1]['temp_max']
            prev_temp_min = historical_data[i-1]['temp_min']
            
            # Smooth temperature changes
            temp_max = (temp_max + prev_temp_max) / 2
            temp_min = (temp_min + prev_temp_min) / 2
        
        historical_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "temp_max": round(temp_max, 1),
            "temp_min": round(temp_min, 1),
            "temp_avg": round((temp_max + temp_min) / 2, 1),
            "precipitation": round(precipitation, 1),
            "humidity": round(random.uniform(60, 90), 1),
        })
    
    return historical_data

def get_weather_alerts(location=None):
    """
    Get weather alerts for the specified location
    
    Args:
        location: Location string (city, coordinates, etc.)
        
    Returns:
        List of dictionaries with weather alerts
    """
    # In a production environment, this would call a real weather API for alerts
    # For this demo, we'll generate some sample alerts
    
    current_date = datetime.now()
    month = current_date.month
    
    alerts = []
    
    # Generate seasonally appropriate alerts with low probability
    if random.random() < 0.3:  # 30% chance of having an alert
        if 3 <= month <= 5:  # Spring
            alerts.append({
                "type": random.choice(["Flood Warning", "Thunderstorm Warning", "Wind Advisory"]),
                "severity": random.choice(["Minor", "Moderate", "Severe"]),
                "time_start": current_date.strftime("%Y-%m-%d %H:%M"),
                "time_end": (current_date + timedelta(hours=random.randint(6, 24))).strftime("%Y-%m-%d %H:%M"),
                "description": "Localized flooding possible. Heavy rain expected. Take precautions."
            })
        elif 6 <= month <= 8:  # Summer
            alerts.append({
                "type": random.choice(["Heat Advisory", "Drought Warning", "Fire Weather Watch"]),
                "severity": random.choice(["Minor", "Moderate", "Severe"]),
                "time_start": current_date.strftime("%Y-%m-%d %H:%M"),
                "time_end": (current_date + timedelta(hours=random.randint(24, 72))).strftime("%Y-%m-%d %H:%M"),
                "description": "Extreme heat expected. Stay hydrated and limit outdoor activities."
            })
        elif 9 <= month <= 11:  # Fall
            alerts.append({
                "type": random.choice(["Frost Advisory", "Wind Advisory", "Flood Watch"]),
                "severity": random.choice(["Minor", "Moderate", "Severe"]),
                "time_start": current_date.strftime("%Y-%m-%d %H:%M"),
                "time_end": (current_date + timedelta(hours=random.randint(6, 36))).strftime("%Y-%m-%d %H:%M"),
                "description": "Potential frost overnight. Protect sensitive crops and plants."
            })
        else:  # Winter
            alerts.append({
                "type": random.choice(["Winter Storm Warning", "Freeze Warning", "Ice Storm Warning"]),
                "severity": random.choice(["Minor", "Moderate", "Severe"]),
                "time_start": current_date.strftime("%Y-%m-%d %H:%M"),
                "time_end": (current_date + timedelta(hours=random.randint(12, 48))).strftime("%Y-%m-%d %H:%M"),
                "description": "Winter storm approaching. Expect hazardous conditions and potential crop damage."
            })
    
    return alerts

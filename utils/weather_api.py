import requests
import json
import os
import logging
from datetime import datetime, timedelta
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional OpenWeatherMap API key from environment variables
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')

def get_current_weather(location):
    """
    Get current weather data for a location
    
    Args:
        location: Location name (e.g., "Countryside, CA") or coordinates (lat,lon)
        
    Returns:
        Dictionary with weather data or None if request failed
    """
    if not OPENWEATHER_API_KEY:
        logger.warning("No OpenWeatherMap API key found. Using simulated weather data.")
        return get_simulated_weather(location)
    
    try:
        # Construct the API URL
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'  # Temperature in Celsius
        }
        
        # Handle coordinates if provided as "lat,lon"
        if ',' in location and all(part.replace('.', '').replace('-', '').isdigit() for part in location.split(',')):
            lat, lon = location.split(',')
            params = {
                'lat': lat.strip(),
                'lon': lon.strip(),
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            del params['q']
        
        # Make the API request
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Format the response
            weather = {
                'location': data['name'],
                'country': data['sys']['country'],
                'coordinates': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                },
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind']['deg'],
                'conditions': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'precipitation': data.get('rain', {}).get('1h', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return weather
        else:
            logger.error(f"Error fetching weather data: {response.status_code} - {response.text}")
            return get_simulated_weather(location)
    
    except Exception as e:
        logger.error(f"Exception in get_current_weather: {e}")
        return get_simulated_weather(location)

def get_weather_forecast(location, days=5):
    """
    Get weather forecast for a location
    
    Args:
        location: Location name (e.g., "Countryside, CA") or coordinates (lat,lon)
        days: Number of days to forecast (max 5 for free tier)
        
    Returns:
        List of dictionaries with forecast data or None if request failed
    """
    if not OPENWEATHER_API_KEY:
        logger.warning("No OpenWeatherMap API key found. Using simulated forecast data.")
        return get_simulated_forecast(location, days)
    
    try:
        # Construct the API URL
        base_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': location,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',  # Temperature in Celsius
            'cnt': min(days * 8, 40)  # 8 measurements per day (3-hour intervals), max 40 for free tier
        }
        
        # Handle coordinates if provided as "lat,lon"
        if ',' in location and all(part.replace('.', '').replace('-', '').isdigit() for part in location.split(',')):
            lat, lon = location.split(',')
            params = {
                'lat': lat.strip(),
                'lon': lon.strip(),
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric',
                'cnt': min(days * 8, 40)
            }
            del params['q']
        
        # Make the API request
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Process and format the forecast data
            forecast = []
            for item in data['list']:
                forecast_time = datetime.fromtimestamp(item['dt'])
                
                # Format each forecast period
                forecast_item = {
                    'date': forecast_time.strftime('%Y-%m-%d'),
                    'time': forecast_time.strftime('%H:%M:%S'),
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'wind_speed': item['wind']['speed'],
                    'wind_direction': item['wind']['deg'],
                    'conditions': item['weather'][0]['main'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'precipitation': item.get('rain', {}).get('3h', 0),
                }
                
                forecast.append(forecast_item)
            
            # Include location information
            location_info = {
                'location': data['city']['name'],
                'country': data['city']['country'],
                'coordinates': {
                    'lat': data['city']['coord']['lat'],
                    'lon': data['city']['coord']['lon']
                }
            }
            
            return {
                'location': location_info,
                'forecast': forecast
            }
        else:
            logger.error(f"Error fetching forecast data: {response.status_code} - {response.text}")
            return get_simulated_forecast(location, days)
    
    except Exception as e:
        logger.error(f"Exception in get_weather_forecast: {e}")
        return get_simulated_forecast(location, days)

def get_historical_weather(location, days=30):
    """
    Get historical weather data for a location
    
    Note: Free tier of OpenWeatherMap API doesn't support historical weather.
    This would require a premium subscription.
    
    For demonstration, we'll generate simulated historical data.
    
    Args:
        location: Location name (e.g., "Countryside, CA")
        days: Number of days of historical data
        
    Returns:
        List of dictionaries with historical weather data
    """
    return get_simulated_historical(location, days)

def get_simulated_weather(location):
    """
    Generate simulated current weather data for demonstration purposes
    
    Args:
        location: Location name
        
    Returns:
        Dictionary with simulated weather data
    """
    # Generate realistic but random weather data
    temp = random.uniform(15, 30)
    conditions = random.choice(['Clear', 'Clouds', 'Rain', 'Drizzle', 'Mist'])
    
    descriptions = {
        'Clear': 'clear sky',
        'Clouds': random.choice(['few clouds', 'scattered clouds', 'broken clouds', 'overcast clouds']),
        'Rain': random.choice(['light rain', 'moderate rain', 'heavy intensity rain']),
        'Drizzle': 'light intensity drizzle',
        'Mist': 'mist'
    }
    
    icons = {
        'Clear': '01d',
        'Clouds': random.choice(['02d', '03d', '04d']),
        'Rain': '10d',
        'Drizzle': '09d',
        'Mist': '50d'
    }
    
    precipitation = 0
    if conditions in ['Rain', 'Drizzle']:
        precipitation = random.uniform(0.5, 10)
    
    # Create the simulated data structure similar to API response
    weather = {
        'location': location.split(',')[0],
        'country': 'US',
        'coordinates': {
            'lat': random.uniform(30, 45),
            'lon': random.uniform(-120, -70)
        },
        'temperature': temp,
        'feels_like': temp - random.uniform(0, 2),
        'humidity': random.uniform(40, 90),
        'pressure': random.uniform(995, 1025),
        'wind_speed': random.uniform(1, 15),
        'wind_direction': random.uniform(0, 359),
        'conditions': conditions,
        'description': descriptions[conditions],
        'icon': icons[conditions],
        'precipitation': precipitation,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'simulated': True
    }
    
    return weather

def get_simulated_forecast(location, days=5):
    """
    Generate simulated forecast data for demonstration purposes
    
    Args:
        location: Location name
        days: Number of days to forecast
        
    Returns:
        Dictionary with simulated forecast data
    """
    # Starting weather conditions
    base_temp = random.uniform(15, 30)
    current_conditions = random.choice(['Clear', 'Clouds', 'Rain', 'Drizzle', 'Mist'])
    
    # Create location info
    location_info = {
        'location': location.split(',')[0],
        'country': 'US',
        'coordinates': {
            'lat': random.uniform(30, 45),
            'lon': random.uniform(-120, -70)
        }
    }
    
    # Generate forecast items (8 per day, 3-hour intervals)
    forecast = []
    
    for day in range(days):
        for hour in [0, 3, 6, 9, 12, 15, 18, 21]:
            # Calculate forecast time
            forecast_time = datetime.now() + timedelta(days=day, hours=hour)
            
            # Evolve weather conditions with some continuity
            # Temperature varies by time of day and has some day-to-day trend
            hour_factor = -2 if hour < 6 or hour > 18 else 2  # Cooler at night, warmer during day
            day_trend = random.uniform(-1, 1)  # Slight trend across days
            temp = base_temp + hour_factor + day_trend + random.uniform(-2, 2)
            
            # Weather conditions sometimes change
            if random.random() < 0.3:  # 30% chance of condition change
                current_conditions = random.choice(['Clear', 'Clouds', 'Rain', 'Drizzle', 'Mist'])
            
            descriptions = {
                'Clear': 'clear sky',
                'Clouds': random.choice(['few clouds', 'scattered clouds', 'broken clouds', 'overcast clouds']),
                'Rain': random.choice(['light rain', 'moderate rain', 'heavy intensity rain']),
                'Drizzle': 'light intensity drizzle',
                'Mist': 'mist'
            }
            
            icons = {
                'Clear': '01d' if 6 <= hour <= 18 else '01n',
                'Clouds': random.choice(['02d', '03d', '04d']) if 6 <= hour <= 18 else random.choice(['02n', '03n', '04n']),
                'Rain': '10d' if 6 <= hour <= 18 else '10n',
                'Drizzle': '09d' if 6 <= hour <= 18 else '09n',
                'Mist': '50d' if 6 <= hour <= 18 else '50n'
            }
            
            precipitation = 0
            if current_conditions in ['Rain', 'Drizzle']:
                precipitation = random.uniform(0.5, 10)
            
            # Create forecast item
            forecast_item = {
                'date': forecast_time.strftime('%Y-%m-%d'),
                'time': forecast_time.strftime('%H:%M:%S'),
                'temperature': temp,
                'feels_like': temp - random.uniform(0, 2),
                'humidity': random.uniform(40, 90),
                'pressure': random.uniform(995, 1025),
                'wind_speed': random.uniform(1, 15),
                'wind_direction': random.uniform(0, 359),
                'conditions': current_conditions,
                'description': descriptions[current_conditions],
                'icon': icons[current_conditions],
                'precipitation': precipitation,
                'simulated': True
            }
            
            forecast.append(forecast_item)
    
    return {
        'location': location_info,
        'forecast': forecast,
        'simulated': True
    }

def get_simulated_historical(location, days=30):
    """
    Generate simulated historical weather data for demonstration purposes
    
    Args:
        location: Location name
        days: Number of days of historical data
        
    Returns:
        List of dictionaries with simulated historical weather data
    """
    # Base weather parameters
    base_temp = random.uniform(15, 30)
    base_humidity = random.uniform(50, 80)
    
    # Generate data for each day
    historical_data = []
    
    for i in range(days):
        # Calculate the date
        date = datetime.now() - timedelta(days=days-i)
        
        # Generate daily weather with some trends and randomness
        # Temperature varies with a small trend over time
        temp_trend = (i / days) * random.uniform(-5, 5)
        daily_temp = base_temp + temp_trend + random.uniform(-3, 3)
        
        # Determine weather conditions (with some continuity)
        if i > 0 and random.random() < 0.7:  # 70% chance of same condition
            conditions = historical_data[-1]['conditions']
        else:
            conditions = random.choice(['Clear', 'Clouds', 'Rain', 'Drizzle', 'Mist'])
        
        descriptions = {
            'Clear': 'clear sky',
            'Clouds': random.choice(['few clouds', 'scattered clouds', 'broken clouds', 'overcast clouds']),
            'Rain': random.choice(['light rain', 'moderate rain', 'heavy intensity rain']),
            'Drizzle': 'light intensity drizzle',
            'Mist': 'mist'
        }
        
        precipitation = 0
        if conditions in ['Rain', 'Drizzle']:
            precipitation = random.uniform(0.5, 20)
        
        # Create the historical data point
        data_point = {
            'date': date.strftime('%Y-%m-%d'),
            'location': location.split(',')[0],
            'temperature': daily_temp,
            'humidity': base_humidity + random.uniform(-10, 10),
            'pressure': random.uniform(995, 1025),
            'wind_speed': random.uniform(1, 15),
            'wind_direction': random.uniform(0, 359),
            'conditions': conditions,
            'description': descriptions[conditions],
            'precipitation': precipitation,
            'simulated': True
        }
        
        historical_data.append(data_point)
    
    return historical_data

def format_weather_for_display(weather_data):
    """
    Format weather data for display in the application
    
    Args:
        weather_data: Weather data dictionary from API or simulation
        
    Returns:
        Dictionary with formatted weather data for display
    """
    if not weather_data:
        return None
    
    # Format current weather data
    if 'timestamp' in weather_data:  # Current weather
        display_data = {
            'location': weather_data.get('location', 'Unknown'),
            'date': datetime.now().strftime('%A, %B %d, %Y'),
            'time': datetime.now().strftime('%I:%M %p'),
            'temperature': f"{round(weather_data.get('temperature', 0))}°C",
            'feels_like': f"{round(weather_data.get('feels_like', 0))}°C",
            'humidity': f"{round(weather_data.get('humidity', 0))}%",
            'wind': f"{round(weather_data.get('wind_speed', 0))} m/s",
            'conditions': weather_data.get('conditions', 'Unknown'),
            'description': weather_data.get('description', ''),
            'icon': weather_data.get('icon', '01d'),
            'precipitation': f"{weather_data.get('precipitation', 0)} mm",
            'simulated': weather_data.get('simulated', False)
        }
        
        return display_data
    
    # Format forecast data
    elif 'forecast' in weather_data:
        location = weather_data.get('location', {}).get('location', 'Unknown')
        
        formatted_forecast = []
        for item in weather_data['forecast']:
            # Parse date and time
            forecast_date = datetime.strptime(f"{item['date']} {item['time']}", '%Y-%m-%d %H:%M:%S')
            
            formatted_item = {
                'date': forecast_date.strftime('%A, %B %d'),
                'time': forecast_date.strftime('%I:%M %p'),
                'temperature': f"{round(item.get('temperature', 0))}°C",
                'humidity': f"{round(item.get('humidity', 0))}%",
                'wind': f"{round(item.get('wind_speed', 0))} m/s",
                'conditions': item.get('conditions', 'Unknown'),
                'description': item.get('description', ''),
                'icon': item.get('icon', '01d'),
                'precipitation': f"{item.get('precipitation', 0)} mm",
                'datetime': forecast_date,  # Include for sorting
                'simulated': item.get('simulated', False)
            }
            
            formatted_forecast.append(formatted_item)
        
        # Group forecast by day
        days = {}
        for item in formatted_forecast:
            day_key = item['date']
            if day_key not in days:
                days[day_key] = []
            days[day_key].append(item)
        
        return {
            'location': location,
            'days': days,
            'simulated': weather_data.get('simulated', False)
        }
    
    # Format historical data
    else:
        formatted_historical = []
        
        for item in weather_data:
            # Parse date
            historical_date = datetime.strptime(item['date'], '%Y-%m-%d')
            
            formatted_item = {
                'date': historical_date.strftime('%A, %B %d'),
                'temperature': f"{round(item.get('temperature', 0))}°C",
                'humidity': f"{round(item.get('humidity', 0))}%",
                'wind': f"{round(item.get('wind_speed', 0))} m/s",
                'conditions': item.get('conditions', 'Unknown'),
                'description': item.get('description', ''),
                'precipitation': f"{item.get('precipitation', 0)} mm",
                'datetime': historical_date,  # Include for sorting
                'simulated': item.get('simulated', False)
            }
            
            formatted_historical.append(formatted_item)
        
        return {
            'location': weather_data[0]['location'] if weather_data else 'Unknown',
            'historical_data': formatted_historical,
            'simulated': weather_data[0].get('simulated', False) if weather_data else False
        }

def get_icon_url(icon_code):
    """
    Get URL for a weather icon
    
    Args:
        icon_code: OpenWeatherMap icon code (e.g., '01d')
        
    Returns:
        URL to the weather icon
    """
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

def calculate_growing_degree_days(weather_data, base_temp=10):
    """
    Calculate Growing Degree Days (GDD) from weather data
    
    GDD = ((Tmax + Tmin) / 2) - Tbase
    where Tbase is the base temperature for crop growth
    
    Args:
        weather_data: List of daily weather data points
        base_temp: Base temperature for crop growth (default 10°C)
        
    Returns:
        Dictionary with GDD statistics
    """
    if not weather_data:
        return None
    
    # Calculate GDD for each day
    gdd_values = []
    dates = []
    
    for day in weather_data:
        # Get temperature values
        temp = day.get('temperature')
        
        # Calculate GDD (daily)
        daily_gdd = max(0, temp - base_temp)
        gdd_values.append(daily_gdd)
        
        # Extract date for the chart
        date = datetime.strptime(day['date'], '%Y-%m-%d') if isinstance(day['date'], str) else day['date']
        dates.append(date)
    
    # Calculate cumulative GDD
    cumulative_gdd = []
    current_sum = 0
    for gdd in gdd_values:
        current_sum += gdd
        cumulative_gdd.append(current_sum)
    
    # Calculate statistics
    gdd_stats = {
        'total_gdd': round(sum(gdd_values), 1),
        'avg_daily_gdd': round(sum(gdd_values) / len(gdd_values), 1) if gdd_values else 0,
        'max_daily_gdd': round(max(gdd_values), 1) if gdd_values else 0,
        'min_daily_gdd': round(min(gdd_values), 1) if gdd_values else 0,
        'chart_data': {
            'dates': dates,
            'daily_gdd': gdd_values,
            'cumulative_gdd': cumulative_gdd
        }
    }
    
    return gdd_stats

def calculate_chill_hours(weather_data, threshold_temp=7.2):
    """
    Calculate Chill Hours from weather data
    
    Chill Hours = number of hours where temperature is below threshold
    
    Args:
        weather_data: List of hourly weather data points
        threshold_temp: Threshold temperature (default 7.2°C / 45°F)
        
    Returns:
        Dictionary with chill hour statistics
    """
    if not weather_data or 'forecast' not in weather_data:
        return None
    
    # Calculate chill hours
    chill_hours = 0
    dates = []
    daily_chill = {}
    
    for item in weather_data['forecast']:
        # Get date and temperature
        date = item['date']
        temp = item.get('temperature')
        
        # Track dates for output
        if date not in dates:
            dates.append(date)
            daily_chill[date] = 0
        
        # Count hours below threshold (each forecast item is typically 3 hours)
        if temp < threshold_temp:
            # Assume each forecast item represents 3 hours
            chill_hours += 3
            daily_chill[date] += 3
    
    # Prepare daily chart data
    daily_values = [daily_chill[date] for date in dates]
    
    # Calculate statistics
    chill_stats = {
        'total_chill_hours': chill_hours,
        'avg_daily_chill': round(chill_hours / len(dates), 1) if dates else 0,
        'max_daily_chill': max(daily_values) if daily_values else 0,
        'min_daily_chill': min(daily_values) if daily_values else 0,
        'chart_data': {
            'dates': dates,
            'daily_chill': daily_values
        }
    }
    
    return chill_stats
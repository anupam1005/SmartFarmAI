import os
import requests
import json
import logging
from datetime import datetime, timedelta
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenWeatherMap API configuration
OWM_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"
ICON_BASE_URL = "https://openweathermap.org/img/wn/"

def get_current_weather(location):
    """
    Get current weather data for a location
    
    Args:
        location: Location name or coordinates
        
    Returns:
        Dictionary with weather data or None if error
    """
    if not OWM_API_KEY:
        logger.warning("No OpenWeatherMap API key found. Using simulated weather data.")
        return _generate_simulated_current_weather(location)
    
    try:
        # Build API URL
        url = f"{OWM_BASE_URL}/weather?q={location}&units=metric&appid={OWM_API_KEY}"
        
        # Make API request
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Extract and format weather data
        return {
            'location': data['name'],
            'timestamp': data['dt'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind']['deg'],
            'conditions': data['weather'][0]['main'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'precipitation': data['rain']['1h'] if 'rain' in data and '1h' in data['rain'] else 0,
            'visibility': data['visibility']
        }
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return _generate_simulated_current_weather(location)

def get_weather_forecast(location, days=5):
    """
    Get weather forecast for a location
    
    Args:
        location: Location name or coordinates
        days: Number of days for forecast (1-5)
        
    Returns:
        Dictionary with forecast data or None if error
    """
    if not OWM_API_KEY:
        logger.warning("No OpenWeatherMap API key found. Using simulated forecast data.")
        return _generate_simulated_forecast(location, days)
    
    try:
        # Build API URL
        url = f"{OWM_BASE_URL}/forecast?q={location}&units=metric&appid={OWM_API_KEY}"
        
        # Make API request
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Process forecast data
        forecast_items = []
        
        # Limit to the requested number of days
        max_timestamp = datetime.now() + timedelta(days=days)
        
        for item in data['list']:
            dt = datetime.fromtimestamp(item['dt'])
            
            if dt > max_timestamp:
                continue
                
            forecast_items.append({
                'timestamp': item['dt'],
                'date': dt.strftime('%Y-%m-%d'),
                'time': dt.strftime('%H:%M'),
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'humidity': item['main']['humidity'],
                'pressure': item['main']['pressure'],
                'wind_speed': item['wind']['speed'],
                'wind_direction': item['wind']['deg'],
                'conditions': item['weather'][0]['main'],
                'description': item['weather'][0]['description'],
                'icon': item['weather'][0]['icon'],
                'precipitation': item['rain']['3h'] if 'rain' in item and '3h' in item['rain'] else 0,
                'clouds': item['clouds']['all']
            })
        
        return {
            'location': data['city']['name'],
            'country': data['city']['country'],
            'forecast': forecast_items
        }
    except Exception as e:
        logger.error(f"Error fetching forecast data: {e}")
        return _generate_simulated_forecast(location, days)

def get_historical_weather(location, days=30):
    """
    Get historical weather data for a location
    
    Args:
        location: Location name or coordinates
        days: Number of days to retrieve (1-60)
        
    Returns:
        List of daily weather data dictionaries or None if error
    """
    # Note: Historical data requires a paid API plan with OpenWeatherMap
    # For this demo, we'll use simulated data
    return _generate_simulated_historical_data(location, days)

def format_weather_for_display(weather_data):
    """
    Format weather data for display in the UI
    
    Args:
        weather_data: Weather data from API
        
    Returns:
        Formatted data dictionary for display
    """
    try:
        # Check if it's current weather or forecast
        if 'forecast' in weather_data:
            # Process forecast data
            result = {
                'location': weather_data['location'],
                'days': {}
            }
            
            # Group by date
            for item in weather_data['forecast']:
                date = item['date']
                
                if date not in result['days']:
                    result['days'][date] = []
                
                # Format individual forecast item
                result['days'][date].append({
                    'date': date,
                    'time': item['time'],
                    'temperature': f"{item['temperature']:.1f}°C",
                    'conditions': item['conditions'],
                    'humidity': f"{item['humidity']}%",
                    'wind': f"{item['wind_speed']:.1f} m/s",
                    'precipitation': f"{item['precipitation']:.1f} mm",
                    'icon': item['icon']
                })
            
            return result
        else:
            # Process current weather
            timestamp = weather_data.get('timestamp')
            
            if isinstance(timestamp, int):
                dt = datetime.fromtimestamp(timestamp)
                date_str = dt.strftime('%Y-%m-%d')
                time_str = dt.strftime('%H:%M')
            else:
                # If timestamp is already formatted or is a string
                now = datetime.now()
                date_str = now.strftime('%Y-%m-%d')
                time_str = now.strftime('%H:%M')
            
            return {
                'location': weather_data['location'],
                'date': date_str,
                'time': time_str,
                'temperature': f"{weather_data.get('temperature', 0):.1f}°C",
                'feels_like': f"{weather_data.get('feels_like', 0):.1f}°C",
                'conditions': weather_data.get('conditions', 'Unknown'),
                'humidity': f"{weather_data.get('humidity', 0)}%",
                'wind': f"{weather_data.get('wind_speed', 0):.1f} m/s",
                'precipitation': f"{weather_data.get('precipitation', 0):.1f} mm",
                'icon': weather_data.get('icon', '01d')
            }
    except Exception as e:
        logger.error(f"Error formatting weather data: {e}")
        return None

def get_icon_url(icon_code):
    """
    Get URL for a weather icon
    
    Args:
        icon_code: OpenWeatherMap icon code
        
    Returns:
        URL for the icon
    """
    return f"{ICON_BASE_URL}{icon_code}@2x.png"

def calculate_growing_degree_days(historical_data, base_temp=10):
    """
    Calculate Growing Degree Days (GDD) from historical weather data
    
    Args:
        historical_data: List of historical weather data entries
        base_temp: Base temperature for GDD calculation (default: 10°C)
        
    Returns:
        Dictionary with GDD metrics
    """
    if not historical_data:
        return None
    
    try:
        # Sort data by date
        sorted_data = sorted(historical_data, key=lambda x: x.get('date', ''))
        
        # Calculate GDD for each day
        daily_gdd = []
        daily_dates = []
        cumulative_gdd = 0
        cumulative_series = []
        
        for day in sorted_data:
            temp = day.get('temperature', 0)
            
            # Basic GDD formula: max(0, avg_temp - base_temp)
            gdd = max(0, temp - base_temp)
            daily_gdd.append(gdd)
            
            # Get date string
            date = day.get('date', '')
            if isinstance(date, str):
                daily_dates.append(date)
            else:
                # Fallback if date is not a string
                daily_dates.append(f"Day {len(daily_dates) + 1}")
            
            # Update cumulative GDD
            cumulative_gdd += gdd
            cumulative_series.append(cumulative_gdd)
        
        # Calculate stats
        return {
            'total_gdd': cumulative_gdd,
            'avg_daily_gdd': sum(daily_gdd) / len(daily_gdd) if daily_gdd else 0,
            'max_daily_gdd': max(daily_gdd) if daily_gdd else 0,
            'min_daily_gdd': min(daily_gdd) if daily_gdd else 0,
            'chart_data': {
                'dates': daily_dates,
                'daily_gdd': daily_gdd,
                'cumulative_gdd': cumulative_series
            }
        }
    except Exception as e:
        logger.error(f"Error calculating GDD: {e}")
        return None

def calculate_chill_hours(forecast_data, threshold_temp=7):
    """
    Calculate chill hours from forecast data
    
    Args:
        forecast_data: Forecast data dictionary
        threshold_temp: Temperature threshold for chill hours (default: 7°C)
        
    Returns:
        Dictionary with chill hours metrics
    """
    if not forecast_data or 'forecast' not in forecast_data:
        return None
    
    try:
        # Extract forecast items
        forecast_items = forecast_data['forecast']
        
        # Group by date
        dates = {}
        
        for item in forecast_items:
            date = item['date']
            
            if date not in dates:
                dates[date] = []
            
            dates[date].append(item)
        
        # Calculate chill hours per day
        daily_chill = []
        date_labels = []
        total_chill_hours = 0
        
        for date, items in dates.items():
            date_labels.append(date)
            
            # Count hours below threshold
            chill_count = sum(1 for item in items if item['temperature'] < threshold_temp)
            
            # Adjust for 3-hour intervals if that's what the API returns
            if len(items) <= 8:  # 24 hours / 3 = 8 entries per day
                chill_count = chill_count * 3
            
            daily_chill.append(chill_count)
            total_chill_hours += chill_count
        
        return {
            'total_chill_hours': total_chill_hours,
            'chart_data': {
                'dates': date_labels,
                'daily_chill': daily_chill
            }
        }
    except Exception as e:
        logger.error(f"Error calculating chill hours: {e}")
        return None

def _generate_simulated_current_weather(location):
    """
    Generate simulated current weather data for demo purposes
    
    Args:
        location: Location name or coordinates
        
    Returns:
        Simulated weather data dictionary
    """
    # Use consistent weather based on the location string hash
    seed = sum(ord(c) for c in location)
    random.seed(seed + datetime.now().day)
    
    # Base temperature on season in northern hemisphere
    month = datetime.now().month
    if 3 <= month <= 5:  # Spring
        base_temp = 15
        temp_range = 10
    elif 6 <= month <= 8:  # Summer
        base_temp = 25
        temp_range = 10
    elif 9 <= month <= 11:  # Fall
        base_temp = 15
        temp_range = 15
    else:  # Winter
        base_temp = 5
        temp_range = 15
    
    temperature = base_temp + (random.random() * temp_range - temp_range/2)
    
    # Weather conditions
    conditions = ["Clear", "Clouds", "Rain", "Drizzle", "Thunderstorm", "Snow", "Mist"]
    weights = [0.4, 0.3, 0.15, 0.05, 0.05, 0.03, 0.02]
    condition = random.choices(conditions, weights=weights)[0]
    
    # Weather icon
    if condition == "Clear":
        icon = "01d"
    elif condition == "Clouds":
        icon = random.choice(["02d", "03d", "04d"])
    elif condition == "Rain":
        icon = random.choice(["09d", "10d"])
    elif condition == "Drizzle":
        icon = "09d"
    elif condition == "Thunderstorm":
        icon = "11d"
    elif condition == "Snow":
        icon = "13d"
    else:  # Mist
        icon = "50d"
    
    # Generate precipitation based on condition
    if condition in ["Rain", "Drizzle", "Thunderstorm"]:
        precipitation = random.random() * 10
        if condition == "Thunderstorm":
            precipitation *= 2
        elif condition == "Drizzle":
            precipitation /= 2
    else:
        precipitation = 0
    
    # Wind speed and direction
    wind_speed = random.random() * 10
    wind_direction = random.randint(0, 359)
    
    # Humidity
    if condition in ["Rain", "Drizzle", "Thunderstorm", "Snow", "Mist"]:
        humidity = random.randint(70, 100)
    else:
        humidity = random.randint(30, 80)
    
    # Pressure
    pressure = random.randint(995, 1025)
    
    # Assemble data
    return {
        'location': location,
        'timestamp': int(datetime.now().timestamp()),
        'temperature': temperature,
        'feels_like': temperature - 2 if temperature < 10 else temperature + 2 if temperature > 25 and humidity > 70 else temperature,
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': wind_speed,
        'wind_direction': wind_direction,
        'conditions': condition,
        'description': f"{condition.lower()}",
        'icon': icon,
        'precipitation': precipitation,
        'visibility': 10000 if condition not in ["Mist", "Snow"] else random.randint(2000, 8000),
        'simulated': True
    }

def _generate_simulated_forecast(location, days=5):
    """
    Generate simulated forecast data for demo purposes
    
    Args:
        location: Location name or coordinates
        days: Number of days for forecast
        
    Returns:
        Simulated forecast data dictionary
    """
    # Use consistent weather patterns based on the location string hash
    seed = sum(ord(c) for c in location)
    random.seed(seed)
    
    # Generate base weather pattern for the period
    base_pattern = _generate_weather_pattern(days)
    
    # Generate forecast items
    forecast_items = []
    
    for day in range(days):
        for hour in range(0, 24, 3):  # 3-hour intervals
            # Date for this forecast item
            dt = datetime.now() + timedelta(days=day, hours=hour)
            
            # Get pattern for this day and apply time variations
            day_pattern = base_pattern[day]
            
            # Temperature variation by time of day
            hour_factor = _get_diurnal_factor(hour)
            temperature = day_pattern['base_temp'] + (day_pattern['temp_range'] * hour_factor)
            
            # Conditions - more likely to rain in afternoon
            rain_chance = day_pattern['rain_chance']
            if 12 <= hour <= 18:
                rain_chance *= 1.5
            
            conditions = _get_conditions_by_chance(rain_chance, day_pattern['cloud_cover'])
            
            # Wind tends to be stronger in the afternoon
            wind_factor = 0.8 + (0.4 * hour_factor)
            wind_speed = day_pattern['wind_speed'] * wind_factor
            
            # Generate icon based on conditions and time
            is_day = 6 <= hour <= 18
            icon = _get_icon_code(conditions, is_day)
            
            # Precipitation
            if conditions in ["Rain", "Drizzle", "Thunderstorm"]:
                precipitation = day_pattern['precip_amount'] * (1 + (hour_factor * 0.5))
            else:
                precipitation = 0
            
            # Create forecast item
            forecast_items.append({
                'timestamp': int(dt.timestamp()),
                'date': dt.strftime('%Y-%m-%d'),
                'time': dt.strftime('%H:%M'),
                'temperature': temperature,
                'feels_like': temperature - 2 if temperature < 10 else temperature + 2 if temperature > 25 and day_pattern['humidity'] > 70 else temperature,
                'humidity': day_pattern['humidity'],
                'pressure': day_pattern['pressure'],
                'wind_speed': wind_speed,
                'wind_direction': day_pattern['wind_direction'],
                'conditions': conditions,
                'description': f"{conditions.lower()}",
                'icon': icon,
                'precipitation': precipitation,
                'clouds': day_pattern['cloud_cover']
            })
    
    return {
        'location': location,
        'country': 'Simulation',
        'forecast': forecast_items,
        'simulated': True
    }

def _generate_simulated_historical_data(location, days=30):
    """
    Generate simulated historical weather data for demo purposes
    
    Args:
        location: Location name or coordinates
        days: Number of days of historical data
        
    Returns:
        List of simulated daily weather data
    """
    # Use location for consistent random generation
    seed = sum(ord(c) for c in location)
    random.seed(seed)
    
    # Generate base weather pattern
    base_pattern = _generate_seasonal_pattern(days)
    
    # Generate daily data
    historical_data = []
    
    for day in range(days):
        # Date for this historical entry
        dt = datetime.now() - timedelta(days=days-day)
        
        # Get pattern for this day
        pattern = base_pattern[day]
        
        # Randomize a bit around the pattern
        temperature = pattern['temp'] + (random.random() * 4 - 2)
        
        # Conditions based on pattern
        conditions = _get_conditions_by_chance(pattern['rain_chance'], pattern['cloud_cover'])
        
        # Set precipitation based on conditions
        if conditions in ["Rain", "Drizzle", "Thunderstorm"]:
            precipitation = pattern['precip'] * (0.5 + random.random())
        else:
            precipitation = 0
        
        # Create historical entry
        historical_data.append({
            'date': dt.strftime('%Y-%m-%d'),
            'location': location,
            'temperature': temperature,
            'humidity': pattern['humidity'],
            'precipitation': precipitation,
            'wind_speed': pattern['wind'] * (0.8 + random.random() * 0.4),
            'wind_direction': pattern['wind_dir'],
            'conditions': conditions,
            'simulated': True
        })
    
    return historical_data

def _generate_weather_pattern(days):
    """
    Generate a consistent weather pattern for multiple days
    
    Args:
        days: Number of days
        
    Returns:
        List of day pattern dictionaries
    """
    # Start with random base conditions
    base_temp = random.randint(10, 25)
    base_wind = random.random() * 5 + 2
    base_cloud = random.randint(0, 100)
    base_rain = min(100, max(0, base_cloud - 30)) / 100  # Rain chance based on cloud cover
    
    # Generate pattern with some day-to-day consistency
    patterns = []
    
    for day in range(days):
        # Evolve the pattern
        base_temp += random.random() * 4 - 2  # Temperature drift
        base_temp = max(5, min(35, base_temp))  # Keep temperature in reasonable range
        
        base_wind = max(1, min(15, base_wind + random.random() * 2 - 1))  # Wind drift
        
        base_cloud = max(0, min(100, base_cloud + random.randint(-20, 20)))  # Cloud drift
        base_rain = min(1.0, max(0, (base_cloud - 30) / 100))  # Rain chance
        
        # Create pattern for this day
        patterns.append({
            'base_temp': base_temp,
            'temp_range': random.randint(5, 15),
            'wind_speed': base_wind,
            'wind_direction': random.randint(0, 359),
            'cloud_cover': base_cloud,
            'rain_chance': base_rain,
            'precip_amount': base_rain * random.randint(5, 20),
            'humidity': 40 + int(base_rain * 40) + random.randint(0, 20),
            'pressure': random.randint(995, 1025)
        })
    
    return patterns

def _generate_seasonal_pattern(days):
    """
    Generate a seasonal weather pattern for historical data
    
    Args:
        days: Number of days
        
    Returns:
        List of day pattern dictionaries
    """
    # Determine season based on current date
    now = datetime.now()
    month = now.month
    
    # Set seasonal parameters
    if 3 <= month <= 5:  # Spring
        base_temp = 15
        temp_trend = 0.1  # Warming trend
        rain_freq = 0.4
    elif 6 <= month <= 8:  # Summer
        base_temp = 25
        temp_trend = 0
        rain_freq = 0.3
    elif 9 <= month <= 11:  # Fall
        base_temp = 15
        temp_trend = -0.1  # Cooling trend
        rain_freq = 0.4
    else:  # Winter
        base_temp = 5
        temp_trend = 0
        rain_freq = 0.5
    
    # Generate weather systems (few days of similar weather)
    patterns = []
    
    # Initialize with random starting point
    current_temp = base_temp + random.randint(-5, 5)
    current_clouds = random.randint(0, 100)
    current_wind = random.random() * 5 + 2
    
    for day in range(days):
        # Apply seasonal trend
        base_effect = base_temp + (days - day) * temp_trend
        
        # Weather systems typically last 3-7 days
        if day % random.randint(3, 7) == 0:
            # New weather system
            current_temp = base_effect + random.randint(-8, 8)
            current_clouds = random.randint(0, 100)
            current_wind = random.random() * 8 + 1
        else:
            # Evolve current system
            current_temp += random.random() * 2 - 1
            current_clouds = max(0, min(100, current_clouds + random.randint(-10, 10)))
            current_wind = max(0, min(15, current_wind + random.random() - 0.5))
        
        # Calculate rain chance based on cloud cover and seasonal frequency
        rain_chance = max(0, min(1, (current_clouds - 30) / 100)) * rain_freq
        
        # Adjust for random storm systems
        if random.random() < 0.1:  # 10% chance of weather event
            if current_temp > 20:
                # Hot weather: chance of thunderstorms
                rain_chance = min(1, rain_chance + 0.4)
            elif current_temp < 5:
                # Cold weather: chance of snow
                rain_chance = min(1, rain_chance + 0.3)
        
        # Create pattern
        patterns.append({
            'temp': current_temp,
            'cloud_cover': current_clouds,
            'rain_chance': rain_chance,
            'wind': current_wind,
            'wind_dir': random.randint(0, 359),
            'humidity': 40 + int(rain_chance * 40) + random.randint(0, 20),
            'precip': rain_chance * random.randint(2, 15)
        })
    
    return patterns

def _get_diurnal_factor(hour):
    """
    Get diurnal temperature variation factor based on hour
    
    Args:
        hour: Hour of day (0-23)
        
    Returns:
        Factor between -1 and 1
    """
    # Coldest at 5 AM, warmest at 3 PM
    return -math.cos((hour - 5) * math.pi / 10) if 5 <= hour <= 15 else -math.cos((hour - 5) * math.pi / 14)

def _get_conditions_by_chance(rain_chance, cloud_cover):
    """
    Determine weather conditions based on rain chance and cloud cover
    
    Args:
        rain_chance: Chance of precipitation (0-1)
        cloud_cover: Cloud cover percentage (0-100)
        
    Returns:
        Weather condition string
    """
    # Roll for precipitation
    if random.random() < rain_chance:
        if random.random() < 0.2:  # 20% of rain is thunderstorm
            return "Thunderstorm"
        elif random.random() < 0.3:  # 30% of remaining rain is drizzle
            return "Drizzle"
        else:
            return "Rain"
    
    # If no precipitation, determine cloud conditions
    if cloud_cover < 20:
        return "Clear"
    elif cloud_cover < 50:
        return "Clouds"  # Few clouds
    else:
        return "Clouds"  # Overcast

def _get_icon_code(condition, is_day):
    """
    Get weather icon code based on condition and time of day
    
    Args:
        condition: Weather condition string
        is_day: Whether it's daytime
        
    Returns:
        OpenWeatherMap icon code
    """
    day_suffix = "d" if is_day else "n"
    
    if condition == "Clear":
        return f"01{day_suffix}"
    elif condition == "Clouds":
        cloud_type = random.choice([2, 3, 4])  # Few, scattered, or broken clouds
        return f"0{cloud_type}{day_suffix}"
    elif condition == "Rain":
        return f"10{day_suffix}"
    elif condition == "Drizzle":
        return f"09{day_suffix}"
    elif condition == "Thunderstorm":
        return f"11{day_suffix}"
    elif condition == "Snow":
        return f"13{day_suffix}"
    else:  # Mist, fog, etc.
        return f"50{day_suffix}"
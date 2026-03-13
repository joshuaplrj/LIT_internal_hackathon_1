"""
Generate synthetic ride-hailing data for PricingGenius challenge
- 6 months of ride data (sampled from 500M rides)
- Competitor price samples
- Weather data, event calendars, traffic data
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

np.random.seed(42)

# City configurations
CITIES = [
    {"name": "New York", "timezone": "America/New_York", "base_multiplier": 1.2, "lat": 40.7128, "lon": -74.0060},
    {"name": "Los Angeles", "timezone": "America/Los_Angeles", "base_multiplier": 1.1, "lat": 34.0522, "lon": -118.2437},
    {"name": "Chicago", "timezone": "America/Chicago", "base_multiplier": 1.0, "lat": 41.8781, "lon": -87.6298},
    {"name": "Houston", "timezone": "America/Chicago", "base_multiplier": 0.9, "lat": 29.7604, "lon": -95.3698},
    {"name": "Phoenix", "timezone": "America/Phoenix", "base_multiplier": 0.85, "lat": 33.4484, "lon": -112.0740},
]

# Base pricing parameters
BASE_FARE = 2.50
PER_MILE = 1.50
PER_MINUTE = 0.25
MINIMUM_FARE = 5.00

# Surge pricing limits
MAX_SURGE = 2.0  # 2x maximum surge


def generate_zones(city: Dict, num_zones: int = 100) -> List[Dict]:
    """Generate geographic zones for a city"""
    zones = []
    center_lat = city["lat"]
    center_lon = city["lon"]
    
    for i in range(num_zones):
        # Create grid of zones around city center
        row = i // 10
        col = i % 10
        
        lat = center_lat + (row - 5) * 0.01 + np.random.normal(0, 0.002)
        lon = center_lon + (col - 5) * 0.01 + np.random.normal(0, 0.002)
        
        zones.append({
            "zone_id": f"{city['name'][:3].upper()}_{i:03d}",
            "name": f"Zone {i+1}",
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "popularity": np.random.beta(2, 5)  # Most zones less popular
        })
    
    return zones


def generate_weather_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Generate hourly weather data"""
    dates = pd.date_range(start=start_date, end=end_date, freq='h')
    
    weather_data = []
    for date in dates:
        # Seasonal temperature
        day_of_year = date.dayofyear
        base_temp = 60 + 20 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Daily variation
        hour_factor = 10 * np.sin(2 * np.pi * (date.hour - 6) / 24)
        
        temperature = base_temp + hour_factor + np.random.normal(0, 5)
        
        # Precipitation (more likely in certain seasons)
        precip_prob = 0.1 + 0.1 * np.sin(2 * np.pi * (day_of_year - 172) / 365)
        precipitation = np.random.exponential(0.1) if np.random.random() < precip_prob else 0
        
        # Weather condition
        if precipitation > 0.5:
            condition = "heavy_rain"
        elif precipitation > 0.1:
            condition = "light_rain"
        elif temperature < 32:
            condition = "snow"
        else:
            condition = "clear"
        
        weather_data.append({
            "timestamp": date.isoformat(),
            "temperature_f": round(temperature, 1),
            "precipitation_in": round(precipitation, 2),
            "condition": condition,
            "wind_speed_mph": round(np.random.exponential(8), 1),
            "humidity": round(np.random.uniform(30, 90), 1)
        })
    
    return pd.DataFrame(weather_data)


def generate_events(start_date: datetime, end_date: datetime, city: str) -> List[Dict]:
    """Generate special events that affect demand"""
    events = []
    current_date = start_date
    
    event_types = [
        {"name": "Concert", "demand_impact": 1.5, "duration_hours": 4},
        {"name": "Sports Game", "demand_impact": 1.8, "duration_hours": 3},
        {"name": "Conference", "demand_impact": 1.3, "duration_hours": 8},
        {"name": "Festival", "demand_impact": 2.0, "duration_hours": 12},
        {"name": "Theater", "demand_impact": 1.2, "duration_hours": 3},
    ]
    
    while current_date < end_date:
        # Random events (about 2 per week)
        if np.random.random() < 0.3:
            event = np.random.choice(event_types)
            event_time = current_date.replace(
                hour=np.random.choice([14, 17, 19, 20]),
                minute=0
            )
            
            events.append({
                "event_id": f"EVT_{len(events):05d}",
                "city": city,
                "name": f"{event['name']} at Venue {np.random.randint(1, 20)}",
                "type": event["name"],
                "start_time": event_time.isoformat(),
                "end_time": (event_time + timedelta(hours=event["duration_hours"])).isoformat(),
                "expected_attendance": int(np.random.lognormal(8, 1)),
                "demand_impact": event["demand_impact"],
                "zone_id": f"{city[:3].upper()}_{np.random.randint(0, 99):03d}"
            })
        
        current_date += timedelta(days=1)
    
    return events


def generate_traffic_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Generate traffic congestion data"""
    dates = pd.date_range(start=start_date, end=end_date, freq='15min')
    
    traffic_data = []
    for date in dates:
        hour = date.hour
        day_of_week = date.dayofweek
        
        # Base congestion
        if day_of_week < 5:  # Weekday
            if 7 <= hour <= 9:  # Morning rush
                base_congestion = 0.7
            elif 16 <= hour <= 19:  # Evening rush
                base_congestion = 0.8
            elif 22 <= hour or hour <= 5:  # Night
                base_congestion = 0.1
            else:
                base_congestion = 0.4
        else:  # Weekend
            if 10 <= hour <= 14:
                base_congestion = 0.5
            elif 19 <= hour <= 23:
                base_congestion = 0.6
            else:
                base_congestion = 0.2
        
        congestion = min(1.0, max(0, base_congestion + np.random.normal(0, 0.1)))
        
        traffic_data.append({
            "timestamp": date.isoformat(),
            "congestion_index": round(congestion, 3),
            "avg_speed_mph": round(30 * (1 - congestion * 0.7), 1),
            "travel_time_multiplier": round(1 + congestion * 0.5, 2)
        })
    
    return pd.DataFrame(traffic_data)


def generate_ride(start_time: datetime, city: Dict, zones: List[Dict], 
                  weather: Dict, traffic: Dict, events: List[Dict]) -> Dict:
    """Generate a single ride"""
    
    # Select origin and destination zones (weighted by popularity)
    zone_weights = [z["popularity"] for z in zones]
    zone_weights = np.array(zone_weights) / sum(zone_weights)
    
    origin_idx = np.random.choice(len(zones), p=zone_weights)
    dest_idx = np.random.choice(len(zones), p=zone_weights)
    while dest_idx == origin_idx:
        dest_idx = np.random.choice(len(zones), p=zone_weights)
    
    origin = zones[origin_idx]
    dest = zones[dest_idx]
    
    # Calculate distance (simplified)
    lat_diff = abs(origin["lat"] - dest["lat"]) * 69  # miles
    lon_diff = abs(origin["lon"] - dest["lon"]) * 54  # miles (approximate)
    distance = np.sqrt(lat_diff**2 + lon_diff**2) + np.random.uniform(0.5, 2)
    distance = round(max(0.5, min(30, distance)), 2)
    
    # Calculate duration based on traffic
    base_duration = distance / 25 * 60  # minutes at 25 mph
    duration = base_duration * traffic.get("travel_time_multiplier", 1)
    duration = round(max(3, duration + np.random.normal(0, 2)), 1)
    
    # Calculate surge multiplier
    hour = start_time.hour
    day_of_week = start_time.weekday()
    
    # Base demand pattern
    if day_of_week < 5:
        if 7 <= hour <= 9 or 16 <= hour <= 19:
            base_demand = 1.3
        elif 22 <= hour or hour <= 2:
            base_demand = 1.2
        else:
            base_demand = 1.0
    else:
        if 22 <= hour or hour <= 3:
            base_demand = 1.4
        else:
            base_demand = 1.0
    
    # Weather impact
    if weather.get("condition") == "heavy_rain":
        weather_multiplier = 1.5
    elif weather.get("condition") == "light_rain":
        weather_multiplier = 1.2
    elif weather.get("condition") == "snow":
        weather_multiplier = 1.6
    else:
        weather_multiplier = 1.0
    
    # Event impact
    event_multiplier = 1.0
    for event in events:
        event_start = datetime.fromisoformat(event["start_time"])
        event_end = datetime.fromisoformat(event["end_time"])
        if event_start <= start_time <= event_end:
            if event["zone_id"] == origin["zone_id"] or event["zone_id"] == dest["zone_id"]:
                event_multiplier = max(event_multiplier, event["demand_impact"])
    
    surge = min(MAX_SURGE, base_demand * weather_multiplier * event_multiplier)
    surge = round(surge + np.random.normal(0, 0.1), 2)
    surge = max(1.0, min(MAX_SURGE, surge))
    
    # Calculate price
    fare = BASE_FARE + (distance * PER_MILE) + (duration * PER_MINUTE)
    fare = max(MINIMUM_FARE, fare * surge * city["base_multiplier"])
    fare = round(fare, 2)
    
    # Driver info
    driver_rating = round(min(5.0, max(3.0, np.random.normal(4.7, 0.3))), 1)
    driver_acceptance_rate = round(min(1.0, max(0.7, np.random.normal(0.9, 0.1))), 2)
    
    # Customer info
    is_new_customer = np.random.random() < 0.1
    customer_lifetime_rides = 0 if is_new_customer else int(np.random.lognormal(3, 1.5))
    
    return {
        "ride_id": f"R{np.random.randint(100000000, 999999999)}",
        "timestamp": start_time.isoformat(),
        "city": city["name"],
        "origin_zone": origin["zone_id"],
        "destination_zone": dest["zone_id"],
        "distance_miles": distance,
        "duration_minutes": duration,
        "surge_multiplier": surge,
        "fare_usd": fare,
        "driver_rating": driver_rating,
        "driver_acceptance_rate": driver_acceptance_rate,
        "is_new_customer": is_new_customer,
        "customer_lifetime_rides": customer_lifetime_rides,
        "weather_condition": weather.get("condition", "clear"),
        "traffic_congestion": traffic.get("congestion_index", 0.5),
        "payment_type": np.random.choice(["credit_card", "debit_card", "paypal", "cash"], 
                                          p=[0.6, 0.2, 0.15, 0.05]),
        "rating": round(min(5, max(1, np.random.normal(4.5, 0.8))), 1) if np.random.random() < 0.7 else None
    }


def generate_competitor_prices(start_date: datetime, end_date: datetime, 
                                city: str) -> pd.DataFrame:
    """Generate competitor pricing data (30% coverage)"""
    dates = pd.date_range(start=start_date, end=end_date, freq='1h')
    
    competitor_data = []
    for date in dates:
        # Only 30% of hours have competitor data
        if np.random.random() < 0.3:
            hour = date.hour
            
            # Competitor base prices (slightly different)
            comp1_base = np.random.uniform(0.9, 1.1)
            comp2_base = np.random.uniform(0.85, 1.15)
            
            # Surge patterns (similar but not identical)
            if 7 <= hour <= 9 or 16 <= hour <= 19:
                surge_prob = 0.6
            elif 22 <= hour or hour <= 2:
                surge_prob = 0.4
            else:
                surge_prob = 0.1
            
            comp1_surge = 1.0 + np.random.exponential(0.3) if np.random.random() < surge_prob else 1.0
            comp2_surge = 1.0 + np.random.exponential(0.25) if np.random.random() < surge_prob else 1.0
            
            competitor_data.append({
                "timestamp": date.isoformat(),
                "city": city,
                "competitor_1_multiplier": round(min(2.5, comp1_base * comp1_surge), 2),
                "competitor_2_multiplier": round(min(2.5, comp2_base * comp2_surge), 2),
                "competitor_1_available": np.random.random() < 0.9,
                "competitor_2_available": np.random.random() < 0.85
            })
    
    return pd.DataFrame(competitor_data)


def main():
    """Generate all data files"""
    print("Generating PricingGenius data...")
    
    # Create directories
    os.makedirs("data/rides", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("data/events", exist_ok=True)
    os.makedirs("data/traffic", exist_ok=True)
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/zones", exist_ok=True)
    
    # Date range (6 months)
    start_date = datetime(2024, 7, 1)
    end_date = datetime(2024, 12, 31)
    
    # Generate data for each city
    all_rides = []
    
    for city in CITIES:
        print(f"\nGenerating data for {city['name']}...")
        
        # Generate zones
        print("  Generating zones...")
        zones = generate_zones(city)
        with open(f"data/zones/{city['name'].lower().replace(' ', '_')}_zones.json", "w") as f:
            json.dump({"city": city["name"], "zones": zones}, f, indent=2)
        
        # Generate weather
        print("  Generating weather data...")
        weather_df = generate_weather_data(start_date, end_date)
        weather_df.to_csv(f"data/weather/{city['name'].lower().replace(' ', '_')}_weather.csv", index=False)
        
        # Generate events
        print("  Generating events...")
        events = generate_events(start_date, end_date, city["name"])
        with open(f"data/events/{city['name'].lower().replace(' ', '_')}_events.json", "w") as f:
            json.dump({"events": events}, f, indent=2)
        
        # Generate traffic
        print("  Generating traffic data...")
        traffic_df = generate_traffic_data(start_date, end_date)
        traffic_df.to_csv(f"data/traffic/{city['name'].lower().replace(' ', '_')}_traffic.csv", index=False)
        
        # Generate competitor prices
        print("  Generating competitor prices...")
        competitor_df = generate_competitor_prices(start_date, end_date, city["name"])
        competitor_df.to_csv(f"data/competitors/{city['name'].lower().replace(' ', '_')}_competitors.csv", index=False)
        
        # Generate rides (sampled - full dataset would be 500M rides)
        print("  Generating rides...")
        num_rides = 100000  # Sample of rides per city
        
        rides = []
        current_time = start_date
        
        for i in range(num_rides):
            if i % 10000 == 0:
                print(f"    Generated {i}/{num_rides} rides...")
            
            # Random time within 6 months
            ride_time = start_date + timedelta(
                seconds=np.random.randint(0, int((end_date - start_date).total_seconds()))
            )
            
            # Get weather for this time
            weather_idx = min(len(weather_df) - 1, 
                            int((ride_time - start_date).total_seconds() / 3600))
            weather = weather_df.iloc[weather_idx].to_dict()
            
            # Get traffic for this time
            traffic_idx = min(len(traffic_df) - 1,
                            int((ride_time - start_date).total_seconds() / 900))
            traffic = traffic_df.iloc[traffic_idx].to_dict()
            
            # Filter events for this time
            active_events = [e for e in events 
                           if datetime.fromisoformat(e["start_time"]) <= ride_time <= datetime.fromisoformat(e["end_time"])]
            
            ride = generate_ride(ride_time, city, zones, weather, traffic, active_events)
            rides.append(ride)
        
        # Save rides
        rides_df = pd.DataFrame(rides)
        rides_df.to_csv(f"data/rides/{city['name'].lower().replace(' ', '_')}_rides.csv", index=False)
        all_rides.extend(rides)
    
    # Save combined rides
    print("\nSaving combined dataset...")
    all_rides_df = pd.DataFrame(all_rides)
    all_rides_df.to_csv("data/all_rides.csv", index=False)
    
    # Generate summary statistics
    summary = {
        "generated_date": datetime.now().isoformat(),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "cities": [c["name"] for c in CITIES],
        "total_rides": len(all_rides),
        "rides_per_city": len(all_rides) // len(CITIES),
        "avg_fare": round(all_rides_df["fare_usd"].mean(), 2),
        "avg_distance": round(all_rides_df["distance_miles"].mean(), 2),
        "avg_duration": round(all_rides_df["duration_minutes"].mean(), 2),
        "avg_surge": round(all_rides_df["surge_multiplier"].mean(), 2),
        "surge_frequency": round((all_rides_df["surge_multiplier"] > 1.0).mean(), 3)
    }
    
    with open("data/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\nData generation complete!")
    print(f"  Total rides: {summary['total_rides']}")
    print(f"  Rides per city: {summary['rides_per_city']}")
    print(f"  Average fare: ${summary['avg_fare']}")
    print(f"  Average distance: {summary['avg_distance']} miles")
    print(f"  Average duration: {summary['avg_duration']} minutes")
    print(f"  Surge frequency: {summary['surge_frequency']*100:.1f}%")


if __name__ == "__main__":
    main()

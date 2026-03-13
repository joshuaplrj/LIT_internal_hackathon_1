"""
Generate synthetic microgrid data for GridBrain challenge
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta


def generate_solar_irradiance(hours: int = 8760) -> pd.DataFrame:
    """Generate hourly solar irradiance data (W/m²)"""
    timestamps = pd.date_range(start='2024-01-01', periods=hours, freq='H')
    
    irradiance = []
    for ts in timestamps:
        hour = ts.hour
        day_of_year = ts.dayofyear
        
        # Seasonal variation (higher in summer)
        seasonal_factor = 0.7 + 0.3 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Daily pattern (bell curve centered at noon)
        if 6 <= hour <= 18:
            daily_factor = np.sin(np.pi * (hour - 6) / 12)
        else:
            daily_factor = 0
        
        # Cloud cover (random)
        cloud_factor = np.random.beta(8, 2)  # Mostly clear
        
        # Calculate irradiance
        max_irradiance = 1000  # W/m²
        irr = max_irradiance * seasonal_factor * daily_factor * cloud_factor
        
        # Add noise
        irr = max(0, irr + np.random.normal(0, 20))
        
        irradiance.append(irr)
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'irradiance_w_m2': irradiance
    })


def generate_wind_speed(hours: int = 8760) -> pd.DataFrame:
    """Generate hourly wind speed data (m/s)"""
    timestamps = pd.date_range(start='2024-01-01', periods=hours, freq='H')
    
    # Weibull distribution parameters for wind
    shape = 2.0
    scale = 7.0
    
    wind_speeds = []
    current_speed = scale
    
    for i in range(hours):
        # Autoregressive component (wind is correlated)
        noise = np.random.normal(0, 1)
        current_speed = 0.8 * current_speed + 0.2 * np.random.weibull(shape) * scale + 0.5 * noise
        current_speed = max(0, min(25, current_speed))  # Clamp to realistic range
        
        wind_speeds.append(current_speed)
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'wind_speed_m_s': wind_speeds
    })


def generate_temperature(hours: int = 8760) -> pd.DataFrame:
    """Generate hourly temperature data (°C)"""
    timestamps = pd.date_range(start='2024-01-01', periods=hours, freq='H')
    
    temperatures = []
    for ts in timestamps:
        hour = ts.hour
        day_of_year = ts.dayofyear
        
        # Seasonal variation
        seasonal = 15 + 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Daily variation
        daily = 5 * np.sin(2 * np.pi * (hour - 6) / 24)
        
        # Random noise
        noise = np.random.normal(0, 2)
        
        temp = seasonal + daily + noise
        temperatures.append(temp)
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'temperature_c': temperatures
    })


def generate_load_demand(hours: int = 8760) -> pd.DataFrame:
    """Generate hourly load demand data (kW)"""
    timestamps = pd.date_range(start='2024-01-01', periods=hours, freq='H')
    
    demands = []
    for ts in timestamps:
        hour = ts.hour
        day_of_week = ts.dayofweek
        
        # Base demand
        base = 400  # kW
        
        # Daily pattern
        if 7 <= hour <= 9:
            daily_factor = 1.3  # Morning peak
        elif 17 <= hour <= 21:
            daily_factor = 1.5  # Evening peak
        elif 22 <= hour or hour <= 5:
            daily_factor = 0.6  # Night low
        else:
            daily_factor = 1.0
        
        # Weekend adjustment
        if day_of_week >= 5:
            daily_factor *= 0.85
        
        # Seasonal (AC in summer, heating in winter)
        day_of_year = ts.dayofyear
        seasonal = 1.0 + 0.2 * np.cos(2 * np.pi * (day_of_year - 172) / 365)
        
        # Random variation
        noise = np.random.normal(1.0, 0.1)
        
        demand = base * daily_factor * seasonal * noise
        demand = max(200, min(800, demand))  # Clamp to realistic range
        
        demands.append(demand)
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'demand_kw': demands
    })


def generate_equipment_specs() -> dict:
    """Generate equipment specifications"""
    return {
        "solar_pv": {
            "peak_capacity_kw": 500,
            "efficiency": 0.18,
            "degradation_rate_yearly": 0.005,
            "area_m2": 2778,
            "tilt_angle": 20,
            "azimuth": 180
        },
        "wind_turbines": {
            "count": 2,
            "rated_power_kw": 250,
            "cut_in_speed_m_s": 3,
            "rated_speed_m_s": 12,
            "cut_out_speed_m_s": 25,
            "hub_height_m": 40
        },
        "battery": {
            "capacity_kwh": 2000,
            "max_power_kw": 500,
            "min_soc": 0.10,
            "max_soc": 0.90,
            "round_trip_efficiency": 0.92,
            "degradation_per_cycle": 0.0001,
            "calendar_degradation_yearly": 0.02,
            "replacement_cost": 200000,
            "lifetime_cycles": 5000
        },
        "diesel_generator": {
            "rated_power_kw": 300,
            "min_load_percent": 0.3,
            "fuel_consumption_l_kwh": 0.25,
            "fuel_cost_per_liter": 1.50,
            "maintenance_cost_per_kwh": 0.05,
            "startup_time_minutes": 5,
            "startup_cost": 10
        },
        "load": {
            "average_demand_kw": 400,
            "peak_demand_kw": 800,
            "max_shedding_hours_per_year": 10,
            "shedding_penalty_per_kwh": 10.0
        }
    }


def main():
    """Generate all data files"""
    print("Generating microgrid data...")
    
    # Generate data
    solar = generate_solar_irradiance()
    wind = generate_wind_speed()
    temp = generate_temperature()
    load = generate_load_demand()
    specs = generate_equipment_specs()
    
    # Save to CSV
    solar.to_csv('data/solar_irradiance.csv', index=False)
    wind.to_csv('data/wind_speed.csv', index=False)
    temp.to_csv('data/temperature.csv', index=False)
    load.to_csv('data/load_demand.csv', index=False)
    
    # Save specs
    with open('data/equipment_specs.json', 'w') as f:
        json.dump(specs, f, indent=2)
    
    print("Data generated successfully!")
    print(f"  Solar: {len(solar)} hours, avg irradiance: {solar['irradiance_w_m2'].mean():.1f} W/m²")
    print(f"  Wind: {len(wind)} hours, avg speed: {wind['wind_speed_m_s'].mean():.1f} m/s")
    print(f"  Temperature: {len(temp)} hours, avg: {temp['temperature_c'].mean():.1f} °C")
    print(f"  Load: {len(load)} hours, avg demand: {load['demand_kw'].mean():.1f} kW")


if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    main()

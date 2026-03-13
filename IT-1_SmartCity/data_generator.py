"""
SmartCity Data Generator

Generates simulated real-time data streams for the digital twin.
"""

import json
import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio


class TrafficSensorGenerator:
    """Generate traffic sensor data"""
    
    def __init__(self, num_sensors: int = 1000):
        self.num_sensors = num_sensors
        self.sensors = self._initialize_sensors()
    
    def _initialize_sensors(self) -> List[Dict]:
        """Initialize sensor locations"""
        sensors = []
        for i in range(self.num_sensors):
            sensors.append({
                "id": f"traffic_{i:04d}",
                "lat": 40.7128 + (random.random() - 0.5) * 0.05,
                "lon": -74.0060 + (random.random() - 0.5) * 0.05,
                "road_type": random.choice(["highway", "arterial", "collector", "local"]),
                "lanes": random.randint(1, 4),
                "speed_limit": random.choice([30, 40, 50, 60, 70])
            })
        return sensors
    
    def generate_reading(self, sensor: Dict, timestamp: datetime) -> Dict:
        """Generate a single sensor reading"""
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Base traffic pattern (rush hours)
        if 7 <= hour <= 9 or 16 <= hour <= 18:
            base_volume = random.randint(800, 1500)
            base_speed = random.uniform(20, 40)
        elif 22 <= hour or hour <= 5:
            base_volume = random.randint(50, 200)
            base_speed = random.uniform(50, 70)
        else:
            base_volume = random.randint(300, 800)
            base_speed = random.uniform(30, 55)
        
        # Weekend adjustment
        if day_of_week >= 5:
            base_volume = int(base_volume * 0.7)
        
        # Road type adjustment
        multipliers = {"highway": 2.0, "arterial": 1.5, "collector": 1.0, "local": 0.5}
        volume = int(base_volume * multipliers.get(sensor["road_type"], 1.0))
        
        # Add noise
        volume = max(0, volume + random.randint(-50, 50))
        speed = max(5, min(sensor["speed_limit"], base_speed + random.uniform(-5, 5)))
        
        # Occupancy (percentage of time sensor is occupied)
        occupancy = min(100, (volume / (sensor["lanes"] * 2000)) * 100)
        
        return {
            "sensor_id": sensor["id"],
            "timestamp": timestamp.isoformat(),
            "volume": volume,
            "speed_kmh": round(speed, 1),
            "occupancy_percent": round(occupancy, 1),
            "lat": sensor["lat"],
            "lon": sensor["lon"]
        }
    
    def generate_batch(self, timestamp: datetime, num_readings: int = 100) -> List[Dict]:
        """Generate batch of sensor readings"""
        readings = []
        selected_sensors = random.sample(self.sensors, min(num_readings, len(self.sensors)))
        
        for sensor in selected_sensors:
            readings.append(self.generate_reading(sensor, timestamp))
        
        return readings


class EnergyGridGenerator:
    """Generate energy grid data"""
    
    def __init__(self):
        self.base_demand = 400  # MW
        self.solar_capacity = 500  # kW
        self.wind_capacity = 500  # kW (2 x 250)
    
    def generate_reading(self, timestamp: datetime) -> Dict:
        """Generate energy grid reading"""
        hour = timestamp.hour
        
        # Demand pattern
        if 7 <= hour <= 9 or 17 <= hour <= 21:
            demand_factor = random.uniform(1.2, 1.5)
        elif 22 <= hour or hour <= 5:
            demand_factor = random.uniform(0.6, 0.8)
        else:
            demand_factor = random.uniform(0.9, 1.1)
        
        total_demand = self.base_demand * demand_factor
        
        # Solar generation (depends on time of day)
        if 6 <= hour <= 18:
            solar_factor = math.sin((hour - 6) * math.pi / 12)
            solar_generation = self.solar_capacity * solar_factor * random.uniform(0.7, 1.0)
        else:
            solar_generation = 0
        
        # Wind generation (random)
        wind_generation = self.wind_capacity * random.uniform(0.1, 0.8)
        
        # Total renewable
        renewable = solar_generation + wind_generation
        
        # Grid from main (diesel backup if needed)
        grid_supply = max(0, total_demand - renewable)
        
        return {
            "timestamp": timestamp.isoformat(),
            "demand_mw": round(total_demand, 2),
            "solar_kw": round(solar_generation, 2),
            "wind_kw": round(wind_generation, 2),
            "renewable_mw": round(renewable / 1000, 2),
            "grid_supply_mw": round(grid_supply, 2),
            "frequency_hz": round(50 + random.uniform(-0.05, 0.05), 3),
            "voltage_kv": round(11 + random.uniform(-0.5, 0.5), 2)
        }


class EmergencyGenerator:
    """Generate emergency call data"""
    
    INCIDENT_TYPES = [
        {"type": "traffic_accident", "severity": "medium", "response_units": 2},
        {"type": "fire", "severity": "high", "response_units": 3},
        {"type": "medical", "severity": "high", "response_units": 1},
        {"type": "power_outage", "severity": "low", "response_units": 1},
        {"type": "flooding", "severity": "medium", "response_units": 2},
        {"type": "gas_leak", "severity": "high", "response_units": 2},
    ]
    
    def generate_incident(self, timestamp: datetime) -> Dict:
        """Generate emergency incident"""
        incident = random.choice(self.INCIDENT_TYPES)
        
        return {
            "id": f"INC-{timestamp.strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            "timestamp": timestamp.isoformat(),
            "type": incident["type"],
            "severity": incident["severity"],
            "lat": 40.7128 + (random.random() - 0.5) * 0.05,
            "lon": -74.0060 + (random.random() - 0.5) * 0.05,
            "response_units_dispatched": incident["response_units"],
            "estimated_response_time_min": random.uniform(3, 12),
            "status": "dispatched"
        }
    
    def should_generate_incident(self) -> bool:
        """Determine if an incident should be generated"""
        # Average ~5 incidents per hour
        return random.random() < 0.014  # ~5/360


class WeatherGenerator:
    """Generate weather data"""
    
    def __init__(self):
        self.base_temp = 20  # Celsius
        self.conditions = ["clear", "partly_cloudy", "cloudy", "rain", "heavy_rain"]
    
    def generate_reading(self, timestamp: datetime) -> Dict:
        """Generate weather reading"""
        hour = timestamp.hour
        
        # Temperature variation
        temp_variation = 5 * math.sin((hour - 6) * math.pi / 12)
        temperature = self.base_temp + temp_variation + random.uniform(-2, 2)
        
        # Weather condition
        condition = random.choices(
            self.conditions,
            weights=[0.4, 0.3, 0.15, 0.1, 0.05]
        )[0]
        
        # Precipitation
        if condition in ["rain", "heavy_rain"]:
            precipitation = random.uniform(1, 10) if condition == "rain" else random.uniform(10, 50)
        else:
            precipitation = 0
        
        return {
            "timestamp": timestamp.isoformat(),
            "temperature_c": round(temperature, 1),
            "humidity_percent": round(random.uniform(40, 80), 1),
            "condition": condition,
            "precipitation_mm": round(precipitation, 1),
            "wind_speed_kmh": round(random.uniform(0, 30), 1),
            "visibility_km": round(random.uniform(5, 20), 1)
        }


class DataStreamGenerator:
    """Main data stream generator"""
    
    def __init__(self):
        self.traffic_gen = TrafficSensorGenerator(1000)
        self.energy_gen = EnergyGridGenerator()
        self.emergency_gen = EmergencyGenerator()
        self.weather_gen = WeatherGenerator()
    
    def generate_all(self, timestamp: datetime) -> Dict:
        """Generate all data types for a timestamp"""
        data = {
            "timestamp": timestamp.isoformat(),
            "traffic": self.traffic_gen.generate_batch(timestamp, 100),
            "energy": self.energy_gen.generate_reading(timestamp),
            "weather": self.weather_gen.generate_reading(timestamp),
            "emergency": None
        }
        
        # Randomly generate emergency incidents
        if self.emergency_gen.should_generate_incident():
            data["emergency"] = self.emergency_gen.generate_incident(timestamp)
        
        return data
    
    async def stream_data(self, callback, interval_seconds: float = 1.0):
        """Stream data continuously"""
        print(f"Starting data stream (interval: {interval_seconds}s)")
        
        while True:
            timestamp = datetime.utcnow()
            data = self.generate_all(timestamp)
            
            await callback(data)
            
            await asyncio.sleep(interval_seconds)


async def print_callback(data: Dict):
    """Print data to console"""
    print(json.dumps(data, indent=2))


async def main():
    """Main entry point"""
    generator = DataStreamGenerator()
    
    print("=== SmartCity Data Generator ===")
    print("Generating simulated data streams...")
    print("Press Ctrl+C to stop\n")
    
    try:
        await generator.stream_data(print_callback, interval_seconds=5.0)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    asyncio.run(main())

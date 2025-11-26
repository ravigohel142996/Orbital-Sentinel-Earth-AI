"""
==============================================================================
Orbital Sentinel - Data Simulator
Generates realistic environmental sensor data for testing and demo
==============================================================================
"""

import asyncio
import random
import uuid
from datetime import datetime
from typing import AsyncGenerator, List, Optional
from loguru import logger

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from backend.models import EnvironmentData, GeoLocation


# Pre-defined locations for simulation (lat, lon, region, country)
SIMULATION_LOCATIONS = [
    (34.0522, -118.2437, "Los Angeles", "USA"),
    (37.7749, -122.4194, "San Francisco", "USA"),
    (40.7128, -74.0060, "New York", "USA"),
    (51.5074, -0.1278, "London", "UK"),
    (35.6762, 139.6503, "Tokyo", "Japan"),
    (48.8566, 2.3522, "Paris", "France"),
    (-33.8688, 151.2093, "Sydney", "Australia"),
    (19.4326, -99.1332, "Mexico City", "Mexico"),
    (28.6139, 77.2090, "New Delhi", "India"),
    (-22.9068, -43.1729, "Rio de Janeiro", "Brazil"),
    (55.7558, 37.6173, "Moscow", "Russia"),
    (39.9042, 116.4074, "Beijing", "China"),
    (1.3521, 103.8198, "Singapore", "Singapore"),
    (-1.2921, 36.8219, "Nairobi", "Kenya"),
    (30.0444, 31.2357, "Cairo", "Egypt"),
    (41.9028, 12.4964, "Rome", "Italy"),
    (-34.6037, -58.3816, "Buenos Aires", "Argentina"),
    (25.2048, 55.2708, "Dubai", "UAE"),
    (52.5200, 13.4050, "Berlin", "Germany"),
    (59.9139, 10.7522, "Oslo", "Norway"),
]

# Risk scenario templates for more interesting simulations
RISK_SCENARIOS = {
    "fire_risk": {
        "temperature": (38, 48),
        "humidity": (5, 25),
        "wind_speed": (30, 80),
        "precipitation": (0, 2),
        "vegetation_index": (-0.2, 0.15),
        "soil_moisture": (5, 20),
    },
    "flood_risk": {
        "temperature": (15, 25),
        "humidity": (85, 100),
        "wind_speed": (20, 60),
        "precipitation": (80, 200),
        "soil_moisture": (85, 100),
        "pressure": (980, 1000),
    },
    "earthquake": {
        "seismic_activity": (3.5, 7.0),
        "temperature": (10, 30),
        "humidity": (40, 70),
    },
    "storm": {
        "wind_speed": (80, 180),
        "pressure": (920, 980),
        "precipitation": (30, 100),
        "humidity": (70, 95),
    },
    "air_quality_crisis": {
        "air_quality_index": (180, 400),
        "temperature": (20, 35),
        "humidity": (30, 60),
        "wind_speed": (0, 15),
    },
    "normal": {
        "temperature": (15, 28),
        "humidity": (40, 70),
        "wind_speed": (5, 25),
        "precipitation": (0, 20),
        "pressure": (1010, 1025),
        "air_quality_index": (30, 80),
        "soil_moisture": (30, 60),
        "vegetation_index": (0.3, 0.8),
    },
}


class DataSimulator:
    """
    Simulates real-time environmental sensor data from multiple global locations.
    Generates realistic patterns including normal conditions and risk scenarios.
    """
    
    def __init__(
        self,
        locations: Optional[List[tuple]] = None,
        risk_probability: float = 0.3
    ):
        """
        Initialize the data simulator.
        
        Args:
            locations: List of (lat, lon, region, country) tuples
            risk_probability: Probability of generating risk scenarios (0-1)
        """
        self.locations = locations or SIMULATION_LOCATIONS
        self.risk_probability = risk_probability
        self._running = False
        self._current_scenario = {}  # Track ongoing scenarios per location
        
        logger.info(f"Data simulator initialized with {len(self.locations)} locations")
    
    def _get_location(self, index: Optional[int] = None) -> GeoLocation:
        """Get a location for data generation"""
        if index is not None:
            loc = self.locations[index % len(self.locations)]
        else:
            loc = random.choice(self.locations)
        
        # Add small random variation to coordinates
        lat = loc[0] + random.uniform(-0.1, 0.1)
        lon = loc[1] + random.uniform(-0.1, 0.1)
        
        return GeoLocation(
            latitude=round(lat, 4),
            longitude=round(lon, 4),
            region=loc[2],
            country=loc[3]
        )
    
    def _get_scenario(self, location_key: str) -> str:
        """Determine scenario for a location"""
        # Check if there's an ongoing scenario
        if location_key in self._current_scenario:
            scenario, remaining = self._current_scenario[location_key]
            if remaining > 0:
                self._current_scenario[location_key] = (scenario, remaining - 1)
                return scenario
            else:
                del self._current_scenario[location_key]
        
        # Determine new scenario based on probability
        if random.random() < self.risk_probability:
            scenario = random.choice([
                "fire_risk", "flood_risk", "earthquake", 
                "storm", "air_quality_crisis"
            ])
            # Set scenario duration (3-8 data points)
            duration = random.randint(3, 8)
            self._current_scenario[location_key] = (scenario, duration)
            return scenario
        
        return "normal"
    
    def _generate_value(
        self,
        min_val: float,
        max_val: float,
        decimals: int = 2
    ) -> float:
        """Generate a random value within range"""
        value = random.uniform(min_val, max_val)
        return round(value, decimals)
    
    def generate_data_point(
        self,
        location: Optional[GeoLocation] = None
    ) -> EnvironmentData:
        """
        Generate a single environmental data point.
        
        Args:
            location: Optional specific location, otherwise random
            
        Returns:
            EnvironmentData object with simulated sensor readings
        """
        if location is None:
            location = self._get_location()
        
        location_key = f"{location.latitude},{location.longitude}"
        scenario = self._get_scenario(location_key)
        params = RISK_SCENARIOS[scenario]
        
        # Generate base data
        data = EnvironmentData(
            timestamp=datetime.utcnow(),
            location=location,
            source="orbital_sentinel_simulator",
        )
        
        # Temperature
        if "temperature" in params:
            data.temperature = self._generate_value(*params["temperature"])
        else:
            data.temperature = self._generate_value(15, 28)
        
        # Humidity
        if "humidity" in params:
            data.humidity = self._generate_value(*params["humidity"])
        else:
            data.humidity = self._generate_value(40, 70)
        
        # Wind speed and direction
        if "wind_speed" in params:
            data.wind_speed = self._generate_value(*params["wind_speed"])
        else:
            data.wind_speed = self._generate_value(5, 25)
        data.wind_direction = self._generate_value(0, 360, 0)
        
        # Precipitation
        if "precipitation" in params:
            data.precipitation = self._generate_value(*params["precipitation"])
        else:
            data.precipitation = self._generate_value(0, 10)
        
        # Pressure
        if "pressure" in params:
            data.pressure = self._generate_value(*params["pressure"])
        else:
            data.pressure = self._generate_value(1010, 1025)
        
        # Air Quality Index
        if "air_quality_index" in params:
            data.air_quality_index = self._generate_value(*params["air_quality_index"], 0)
        else:
            data.air_quality_index = self._generate_value(30, 80, 0)
        
        # Seismic activity
        if "seismic_activity" in params:
            data.seismic_activity = self._generate_value(*params["seismic_activity"])
        else:
            data.seismic_activity = self._generate_value(0, 2.5)
        
        # Soil moisture
        if "soil_moisture" in params:
            data.soil_moisture = self._generate_value(*params["soil_moisture"])
        else:
            data.soil_moisture = self._generate_value(30, 60)
        
        # Vegetation index
        if "vegetation_index" in params:
            data.vegetation_index = self._generate_value(*params["vegetation_index"])
        else:
            data.vegetation_index = self._generate_value(0.3, 0.8)
        
        return data
    
    async def stream_data(
        self,
        interval_seconds: float = 5.0,
        max_points: Optional[int] = None
    ) -> AsyncGenerator[EnvironmentData, None]:
        """
        Generate a continuous stream of environmental data.
        
        Args:
            interval_seconds: Time between data points
            max_points: Maximum number of points to generate (None for infinite)
            
        Yields:
            EnvironmentData objects
        """
        self._running = True
        count = 0
        location_index = 0
        
        logger.info(f"Starting data stream (interval: {interval_seconds}s)")
        
        while self._running:
            if max_points is not None and count >= max_points:
                break
            
            # Generate data for rotating locations
            location = self._get_location(location_index)
            data = self.generate_data_point(location)
            
            yield data
            
            count += 1
            location_index = (location_index + 1) % len(self.locations)
            
            await asyncio.sleep(interval_seconds)
        
        logger.info(f"Data stream stopped after {count} points")
    
    def stop(self):
        """Stop the data stream"""
        self._running = False
    
    def generate_batch(self, count: int = 10) -> List[EnvironmentData]:
        """
        Generate a batch of data points.
        
        Args:
            count: Number of data points to generate
            
        Returns:
            List of EnvironmentData objects
        """
        return [
            self.generate_data_point(self._get_location(i))
            for i in range(count)
        ]


# Module-level instance for convenience
_simulator = None


def get_simulator() -> DataSimulator:
    """Get or create the default simulator instance"""
    global _simulator
    if _simulator is None:
        _simulator = DataSimulator()
    return _simulator


async def demo_stream():
    """Demo function to test the simulator"""
    simulator = DataSimulator(risk_probability=0.4)
    
    async for data in simulator.stream_data(interval_seconds=1, max_points=5):
        print(f"\n--- {data.timestamp.isoformat()} ---")
        print(f"Location: {data.location.region}, {data.location.country}")
        print(f"  Coords: ({data.location.latitude}, {data.location.longitude})")
        print(f"  Temp: {data.temperature}°C, Humidity: {data.humidity}%")
        print(f"  Wind: {data.wind_speed} km/h @ {data.wind_direction}°")
        print(f"  AQI: {data.air_quality_index}, Seismic: {data.seismic_activity}")


if __name__ == "__main__":
    asyncio.run(demo_stream())

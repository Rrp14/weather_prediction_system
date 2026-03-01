import random
import math
import hashlib
from datetime import datetime

class ClimateEngine:

    def __init__(self, sensors=1000):
        self.sensors = sensors

        # Multi-city simulation
        self.cities = [
            {
    "name": "Bangalore",
    "lat": 12.97,
    "lon": 77.59,
    "base_temp": 28,
    "alerts": [
        

        # Kannada
        "ಉಷ್ಣತೆಯ ಅಲೆ ಎಚ್ಚರಿಕೆ",        # Heatwave warning
        "ಚಂಡಮಾರುತ ಎಚ್ಚರಿಕೆ",           # Cyclone alert
        "ಭಾರಿ ಮಳೆ ಎಚ್ಚರಿಕೆ",           # Heavy rain warning

        # Hindi (optional but realistic)
        "चक्रवात चेतावनी",
        "भारी वर्षा चेतावनी"
    ]
},
            {
                "name": "Paris",
                "lat": 48.85,
                "lon": 2.35,
                "base_temp": 18,
                "alerts": [
                    "Vague de chaleur",
                    "Tempête sévère",
                    "Inondation"
                ]
            },
            {
                "name": "Madrid",
                "lat": 40.41,
                "lon": -3.70,
                "base_temp": 25,
                "alerts": [
                    "Tormenta severa",
                    "Ola de calor",
                    "Inundación"
                ]
            },
            {
                "name": "New York",
                "lat": 40.71,
                "lon": -74.00,
                "base_temp": 20,
                "alerts": [
                    "Storm warning",
                    "Flood alert",
                    "Heat advisory"
                ]
            }
        ]

    def anonymize(self, sensor_id):
        return hashlib.sha256(sensor_id.encode()).hexdigest()

    def generate_reading(self, sensor_id):

        city = random.choice(self.cities)

        hour = datetime.utcnow().hour
        daily_wave = 5 * math.sin(hour / 24 * 2 * math.pi)

        temperature = city["base_temp"] + daily_wave + random.uniform(-2, 2)
        humidity = random.uniform(35, 90)
        wind_speed = random.uniform(0, 40)

        if random.random() < 0.01:
            temperature += random.uniform(5, 12)

        if random.random() < 0.02:
            return None

        alert = random.choice(city["alerts"]) if random.random() < 0.05 else None

        return {
            "sensor_id": self.anonymize(sensor_id),
            "timestamp": datetime.utcnow().isoformat(),
            "location": {
                "lat": city["lat"] + random.uniform(-0.2, 0.2),
                "lon": city["lon"] + random.uniform(-0.2, 0.2)
            },
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "wind_speed": round(wind_speed, 2),
            "alert": alert
        }
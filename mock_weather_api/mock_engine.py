import random
import math
import hashlib
from datetime import datetime
from faker import Faker

fake = Faker()

class ClimateEngine:

    def __init__(self, sensors=1000):
        self.sensors = sensors
        self.base_temp = 28

    def anonymize(self, sensor_id):
        return hashlib.sha256(sensor_id.encode()).hexdigest()

    def generate_reading(self, sensor_id):

        hour = datetime.utcnow().hour
        daily_wave = 5 * math.sin(hour/24 * 2 * math.pi)

        temperature = self.base_temp + daily_wave + random.uniform(-2, 2)
        humidity = random.uniform(35, 90)
        wind_speed = random.uniform(0, 40)

        # Inject anomaly
        if random.random() < 0.01:
            temperature += random.uniform(5, 12)

        # Simulate device failure
        if random.random() < 0.02:
            return None

        multilingual_alerts = [
            "Heatwave warning",
            "चक्रवात चेतावनी",
            "Cyclone Alert",
            "Vague de chaleur",
            "Tormenta severa"
        ]

        return {
            "sensor_id": self.anonymize(sensor_id),
            "timestamp": datetime.utcnow().isoformat(),
            "location": {
                "lat": 12.97 + random.uniform(-0.5, 0.5),
                "lon": 77.59 + random.uniform(-0.5, 0.5)
            },
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "wind_speed": round(wind_speed, 2),
            "alert": random.choice(multilingual_alerts) if random.random() < 0.05 else None
        }
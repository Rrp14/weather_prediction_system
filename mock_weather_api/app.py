import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mock_engine import ClimateEngine
from kafka_producer import send_to_kafka

engine = ClimateEngine(sensors=5000)

async def produce():
    while True:
        for i in range(engine.sensors):
            data = engine.generate_reading(f"SENSOR_{i}")
            if data:
                send_to_kafka("climate-data", data)
        await asyncio.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(produce())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "running"}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Inicialización de FastAPI
app = FastAPI()

# Conexión a MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["engine_events_db"]
collection = db["events"]

# Esquema de validación con Pydantic
class Location(BaseModel):
    city: str
    state: str
    country: str
    lat: float
    lon: float

class EngineParameters(BaseModel):
    rpm: float
    odometer: float
    speed: float
    fuel_level: float
    cruise_control_active: bool
    cruise_control_set_speed: float

class Data(BaseModel):
    powerunit_vin: str
    powerunit_id: str
    hardware_type: str
    ignition: bool
    wheels_in_motion: bool
    location: Location
    engine_parameters: EngineParameters

class Event(BaseModel):
    event: str
    count: int
    timestamp: int
    data: List[Data]

# Endpoint para enviar datos
@app.post("/events/")
async def create_event(event: Event):
    # Inserción en MongoDB
    document = event.dict()
    document["created_at"] = datetime.utcnow()  # Añade un timestamp
    result = await collection.insert_one(document)
    if result.inserted_id:
        return {"message": "Event stored successfully", "id": str(result.inserted_id)}
    raise HTTPException(status_code=500, detail="Failed to store event")

# Endpoint para obtener todos los eventos
@app.get("/events/")
async def get_events():
    events = []
    async for event in collection.find():
        event["_id"] = str(event["_id"])  # Convierte ObjectId a string
        events.append(event)
    return events

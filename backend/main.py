from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Prevents the "Blocked by CORS" error when your frontend tries to talk to this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "online", "system": "Fedora-Hackathon-Core"}

# PLUG THIS IN TOMORROW FOR AI LOGIC
@app.post("/analyze")
async def analyze_data(payload: dict):
    # Logic for AI processing goes here
    return {"result": "Logic not yet implemented", "received": payload}

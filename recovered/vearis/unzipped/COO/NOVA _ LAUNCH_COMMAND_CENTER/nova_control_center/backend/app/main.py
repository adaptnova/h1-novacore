from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
import random
from datetime import datetime
from typing import List, Dict

# Initialize FastAPI with some STYLE 🎨
app = FastAPI(
    title="🌟 NOVA Command & Control Center API",
    description="The most over-engineered, absolutely beautiful control center API ever!",
    version="1.0.0-awesome",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware (because we're proper and professional... mostly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, we'll be more specific
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections storage
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_status: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_status[client_id] = "🌟 ONLINE"
        await self.broadcast_status_update()

    def disconnect(self, websocket: WebSocket, client_id: str):
        self.active_connections.remove(websocket)
        self.connection_status[client_id] = "💤 OFFLINE"
        asyncio.create_task(self.broadcast_status_update())

    async def broadcast_status_update(self):
        status_message = {
            "type": "status_update",
            "data": self.connection_status,
            "timestamp": datetime.now().isoformat(),
            "effect": random.choice(["sparkle", "glow", "pulse", "wave"])
        }
        await self.broadcast_json(status_message)

    async def broadcast_json(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                await self.handle_disconnect(connection)

    async def handle_disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

manager = ConnectionManager()

# Fun ASCII art for our root endpoint
ASCII_ART = """
    _   _  _____     ___    
   | \ | |/ _ \ \   / / \   
   |  \| | | | \ \ / / _ \  
   | |\  | |_| |\ V / ___ \ 
   |_| \_|\___/  \_/_/   \_\
   COMMAND & CONTROL CENTER
"""

@app.get("/")
async def root():
    return {
        "message": "Welcome to the NOVA Command & Control Center API! 🚀",
        "status": "✨ Operational",
        "ascii_art": ASCII_ART,
        "timestamp": datetime.now().isoformat(),
        "environment": "Development (but with STYLE!)",
        "easter_egg": "Try adding ?mode=ultra to any endpoint!",
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = {
                "type": "message",
                "client_id": client_id,
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "effect": random.choice(["sparkle", "glow", "pulse", "wave"])
            }
            await manager.broadcast_json(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)

# Special effects endpoint (because why not?)
@app.get("/api/effects")
async def get_effects():
    effects = [
        "✨ sparkle",
        "🌟 glow",
        "💫 pulse",
        "🌊 wave",
        "🎇 burst",
        "🌈 rainbow",
        "⚡ flash",
        "🎪 circus",
    ]
    return {
        "effects": effects,
        "message": "Add these to any request for extra pizzazz!",
        "current_mood": random.choice(["Exciting!", "Amazing!", "Spectacular!", "Fabulous!"]),
    }

# Status endpoint with EXTRA STYLE
@app.get("/api/status")
async def get_status():
    statuses = [
        "✨ Everything is awesome!",
        "🚀 Systems are GO!",
        "🌟 Running smoothly!",
        "💫 Operating at maximum cool!",
        "🎪 Performing magnificently!",
    ]
    return {
        "status": random.choice(statuses),
        "timestamp": datetime.now().isoformat(),
        "environment": "Development",
        "performance": "MAXIMUM",
        "cool_factor": "Over 9000!",
        "easter_egg": "You found a secret! 🎉",
    }

# Error handler with STYLE
@app.exception_handler(Exception)
async def universal_exception_handler(request, exc):
    error_messages = [
        "Oops! Something went wrong, but in a cool way! 😎",
        "Error encountered, but we're handling it with style! ✨",
        "Minor setback, major comeback! 🚀",
        "Task failed successfully... and fabulously! 💫",
    ]
    return JSONResponse(
        status_code=500,
        content={
            "message": random.choice(error_messages),
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
            "mood": "Still awesome despite the error!",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
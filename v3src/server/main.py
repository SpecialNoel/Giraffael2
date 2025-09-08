# server.py

# python -m v3src.server.main

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from v3src.server.services.connection_manager import manager
from v3src.server.routers import websocket_routes, file_routes, message_routes, room_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: manager connects to Redis and starts Pub/Sub services
    await manager.start()
    yield
    # Shutdown: manager stops Pub/Sub services and closes connection to Redis
    await manager.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(websocket_routes.router)
app.include_router(file_routes.router)
app.include_router(message_routes.router)
app.include_router(room_routes.router)

if __name__=='__main__':
    # Run a uvicorn web server
    # server_ip = '10.0.0.33'
    server_ip = '10.0.0.99'
    uvicorn.run(app, host=server_ip, port=5001)

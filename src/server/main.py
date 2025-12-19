# server.py

# python -m src.server.main

import uvicorn
from redis import Redis
import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.server.app.services.connection_manager import manager
from src.server.app.routers import websocket_routes, file_routes, message_routes, room_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: manager connects to Redis and starts Pub/Sub services
    await manager.start()
    yield
    # Shutdown: manager stops Pub/Sub services and closes connection to Redis
    await manager.stop()

# Handle the problem where the API might connect immediately after startup (i.e. before Redis)
for _ in range(10):
    try:
        # 
        redis_client = Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        redis_client.ping()
        break
    except Exception:
        time.sleep(1)

app = FastAPI(lifespan=lifespan)

app.include_router(websocket_routes.router)
app.include_router(file_routes.router)
app.include_router(message_routes.router)
app.include_router(room_routes.router)

if __name__=='__main__':
    # Run a uvicorn web server
    uvicorn.run(app, host='0.0.0.0', port=5001)

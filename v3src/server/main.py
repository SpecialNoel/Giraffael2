# server.py

# python -m v3src.server.main

import uvicorn
from fastapi import FastAPI
from v3src.server.routers import websocket_routes, file_routes, message_routes, room_routes

app = FastAPI()

app.include_router(websocket_routes.router)
app.include_router(file_routes.router)
app.include_router(message_routes.router)
app.include_router(room_routes.router)

if __name__=='__main__':
    # Run a uvicorn web server
    uvicorn.run(app, host='10.0.0.99', port=5001)

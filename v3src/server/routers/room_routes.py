# room_routes.py

from fastapi import APIRouter
from v3src.server.schemas.client_obj import Client_Obj
from v3src.server.schemas.definitions import RoomRequest
from v3src.server.services.room_service import create_room_with_room_code, join_room_with_room_code, check_room_existence

router = APIRouter()

# FastAPI endpoint for handling a 'create room' request from a client
@router.post('/room/create')
async def create_room(request: RoomRequest):
    # Retrieve room code and username
    room_code = request.room_code
    username = request.username
    
    # Check MongoDB for room existence
    if check_room_existence(room_code):
        data = {'message': f'Failed to create room. Room {room_code} already exists.',
                'status': 'failed'}
        return data    
    
    # Generate ClientObj and uuid for this client
    client_obj = Client_Obj(username)
    uuid = client_obj.get_uuid()
    
    # Create room in MongoDB
    if create_room_with_room_code(room_code, uuid, username):
        data = {'message': f'Successfully created room {room_code}.',
                'status': 'succeeded',
                'uuid': uuid}
        return data
    else:
        data = {'message': f'Failed to create room. Room {room_code} already exists.',
                'status': 'failed'}
        return data

# FastAPI endpoint for handling a 'join room' request from a client
@router.post('/room/join')
def join_room(request: RoomRequest):
    room_code = request.room_code
    
    return join_room_with_room_code(room_code)

# room_service.py

from src.server.app.schemas.client_obj import Client_Obj
from src.server.app.db.mongo.room_ops.create_op import create_room_in_db
from src.server.app.db.mongo.room_ops.join_op import join_room_in_db

# Create a room with given room code (Create-only operation)
def create_room_with_room_code(room_code: str):
    # Create a room in MongoDB with given room code
    return create_room_in_db(room_code)

# Join the client to the given room (Join-only operation)
def join_room_with_room_code(roomCode: str, client_obj: Client_Obj): 
    # Join to a room in MongoDB with given room code
    return join_room_in_db(roomCode, client_obj)

# Get the online status of clients in Redis
async def get_online_status_of_clients_in_room(redis, room_code):
    # Get all uuids from the given room in Redis
    uuids = await redis.smembers(f'room_code:{room_code}:client_list')
    result = {}
    for uuid in uuids:
        presence = await redis.get(f'presence:{room_code}:{uuid}')
        result[uuid] = 'online' if presence else 'offline'
    return result
    
# Delete the room in Redis (useful for removing 'zombie clients')
async def delete_room(redis, room_code):
    await redis.delete(f'room_code:{room_code}:client_list')
    print(f'Deleted room [{room_code}] in Redis.')
    return       

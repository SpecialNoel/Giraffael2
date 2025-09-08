# join_op.py

from v3src.server.mongo_db.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.mongo_db.mongodb_initiator import rooms_collection

# Join the client to a given room in MongoDB
def join_room_in_db(room_code, client_obj):
    uuid = client_obj.get_uuid()
    username = client_obj.get_username()

    # Check room code validness
    if not room_code_exists_in_collection(room_code):
        print(f'Error in add_client_to_list().'+
              f'Client [{uuid}] tries to join room [{room_code}] which does not exist.')
        return False
    
    client_info = {'uuid': uuid, 'username': username}
    
    # Add client into client list of this room
    try:
        rooms_collection.update_one(
            {'roomCode': room_code},
            {'$push': {'clientList': client_info}}
        )
        print(f'Successfully added client [{uuid}] to the room [{room_code}]')
    except Exception:
        print('Error in add_client_to_list().'+
              f'Failed to add the client [{uuid}] into client list in room [{room_code}].')
        return False
    return True

# add_op.py

import datetime
from v3src.server.mongo_db.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.mongo_db.mongodb_initiator import rooms_collection

def add_client_to_list(clientObj, roomCode):
    clientInfo = clientObj.to_dict()

    # Check room code validness
    if not room_code_exists_in_collection(roomCode):
        print(f'Error in add_client_to_list(). Room code [{roomCode}] does not exist.')
        print(f'Client info: [{clientInfo}]. Room code: [{roomCode}].')
        return
    
    # Get current time
    current_time = datetime.datetime.now(tz=datetime.timezone.utc)
    
    # Add client into client list of this room
    try:
        rooms_collection.update_one(
            {'roomCode': roomCode},
            {'$push': {'clientList': {'clientInfo': clientInfo, 
                                      'joined': current_time}}}
        )
        print(f'Successfully added client to the room')
        print(f'Client info: [{clientInfo}]. Room code: [{roomCode}].')
    except Exception as e:
        print(f'Exception encountered: [{e}].')
        print('Error in add_client_to_list(). Failed to add the client into client list.')
        print(f'Client info: [{clientInfo}]. Room code: [{roomCode}].')
        return
    return 

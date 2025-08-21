# add_op.py

import datetime
from bson import ObjectId
from v3src.server.database.msg_ops.general_op import roomCode_to_roomID
from v3src.server.database.mongodb_initiator import rooms_collection, user_statuses_collection

def add_client_to_list(clientObj, roomCode):
    roomID = roomCode_to_roomID(roomCode)

    if roomID:
        rooms_collection.update_one(
            {'_id': ObjectId(roomID)},
            {'$push': {'clientList': clientObj.to_dict()}}
        )
        print(f'Successfully added client [{clientObj.get_address()}] to the clientList of room with roomCode [{roomCode}].')

        # Update the 
        current_time = datetime.datetime.now(tz=datetime.timezone.utc)        
        user_statuses_collection.update_one(
            {'_id': ObjectId(roomID)},
            {'$push': {'last_activity_timestamp ': current_time}}
            {}
        )
        print(f'')
    else: 
        print(f'Error in add_client_to_list(). Room with roomCode [{roomCode}] does not exist.')
    return 

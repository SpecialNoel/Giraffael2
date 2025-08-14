# add_op.py

from bson import ObjectId
from v3src.server.database.msg_ops.general_op import roomCode_to_roomID
from v3src.server.database.mongodb_initiator import rooms_collection

def add_client_to_list(clientObj, roomCode):
    roomID = roomCode_to_roomID(roomCode)

    if roomID:
        rooms_collection.update_one(
            {'_id': ObjectId(roomID)},
            {'$push': {'clientList': clientObj.to_dict()}}
        )
        print(f'Successfully added client [{clientObj.get_address()}] to the clientList of room with roomCode [{roomCode}].')
    else: 
        print(f'Error in add_client_to_list(). Room with roomCode [{roomCode}] does not exist.')
    return 

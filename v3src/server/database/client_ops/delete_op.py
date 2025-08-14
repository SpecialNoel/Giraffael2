# delete_op.py

from bson import ObjectId
from v3src.server.database.msg_ops.general_op import roomCode_to_roomID
from v3src.server.database.mongodb_initiator import rooms_collection

def delete_client_from_list(address, roomCode):
    roomID = roomCode_to_roomID(roomCode)

    if roomID:
        rooms_collection.update_one(
            {'_id': ObjectId(roomID)},
            {'$pull': {'clientList': {'address': address}}}
        )
        print(f'Successfully deleted client with address [{address}] from the clientList of room with roomCode [{roomCode}].')
    else: 
        print(f'Error in delete_client_to_list(). Room with roomCode [{roomCode}] does not exist.')
    return

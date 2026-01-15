# list_op.py

from server_only.mongodb_related.msg_ops.general_op import roomCode_to_roomID
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from bson import ObjectId

def list_clients(roomCode):
    roomID = roomCode_to_roomID(roomCode)

    if roomID:
        print(f'Clients in room with roomCode [{roomCode}]:')
        room = rooms_collection.find_one(
            {'_id': ObjectId(roomID)}
        )
        clientList = room['clientList']
        for client in clientList:
            print(f'--uuid:[{client['uuid']}]. address:[{client['address']}]. username:[{client['username']}]')
    else: 
        print(f'Error in add_client_to_list(). Room with roomCode [{roomCode}] does not exist.')
    return 

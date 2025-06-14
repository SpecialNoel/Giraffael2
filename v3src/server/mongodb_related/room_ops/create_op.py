# create_op.py

from v3src.server.mongodb_related.msg_ops.general_op import roomCode_to_roomID
from v3src.server.mongodb_related.mongodb_initiator import rooms_collection

def create_room(roomCode, roomName='NewRoom'):
    if roomCode_to_roomID(roomCode) != None:
        print(f'Error in create_room(). Room with roomCode [{roomCode}] already exists.')
        return
    room_data = {
        'roomCode': roomCode,
        'roomName': roomName,
        'clientList': [],
        'msgList': [],
        'fileList': []
    }
    roomInsertedID = rooms_collection.insert_one(room_data).inserted_id
    print(f'Created room in DB with roomCode [{roomCode}]. ' +
          f'roomID is [{roomInsertedID}].')
    return

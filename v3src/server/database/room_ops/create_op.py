# create_op.py

from v3src.server.database.msg_ops.general_op import roomCode_to_roomID
from v3src.server.database.mongodb_initiator import rooms_collection, user_statuses_collection

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
    
    roomID = roomCode_to_roomID(roomCode)
    room_data_for_online_status = {
        'roomID': roomID,
        'userStatuses': {}
    }
    userStatusListInsertedID = user_statuses_collection.insert_one(roomID).inserted_id
    print(f'userStatusListInsertedID: [{userStatusListInsertedID}].')
    print(f'Created user status list in room with ID [{roomID}].')
    return

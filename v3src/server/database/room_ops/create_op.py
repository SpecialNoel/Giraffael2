# create_op.py

from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.database.mongodb_initiator import rooms_collection, user_statuses_collection

def create_room(roomCode, roomName='NewRoom'):
    if room_code_exists_in_collection(roomCode):
        print(f'Error in create_room(). Room [{roomCode}] already exists.')
        return
    room_data = {
        'roomCode': roomCode,
        'roomName': roomName,
        'clientList': [],
        'msgList': [],
        'fileList': []
    }
    roomInsertedID = rooms_collection.insert_one(room_data).inserted_id
    print(f'Created room in DB with room code [{roomCode}]. ' +
          f'Room code is [{roomInsertedID}].')
    
    room_data_for_online_status = {
        'roomCode': roomCode,
        'userStatuses': {}
    }
    userStatusListInsertedID = user_statuses_collection.insert_one(roomCode).inserted_id
    print(f'userStatusListInsertedID: [{userStatusListInsertedID}].')
    print(f'Created user status list in room with ID [{roomCode}].')
    return

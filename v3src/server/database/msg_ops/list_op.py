# list_op.py

from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.database.mongodb_initiator import rooms_collection

# List out all messages sent over this room
def list_msg_history(roomCode):
    if room_code_exists_in_collection(roomCode):
        print(f'Msg history stored in room with roomCode [{roomCode}]:')
        room = rooms_collection.find_one(
            {'roomCode': roomCode}
        )
        msgMetadatas = room['msgList']
        for msgMetadata in msgMetadatas:
            print(f'[{msgMetadata['senderName']}]: [{msgMetadata['message']}]')
    else:
        print(f'Error in list_msg(). Room with roomCode [{roomCode}] does not exist.')
    return

def get_msg_history(roomCode):
    if room_code_exists_in_collection(roomCode):
        print(f'Msg history stored in room with roomCode [{roomCode}]:')
        room = rooms_collection.find_one(
            {'roomCode': roomCode}
        )
        msgHistory = []
        msgMetadatas = room['msgList']
        for msgMetadata in msgMetadatas:
            msgHistory.append({msgMetadata['senderName']: msgMetadata['message']})
        return msgHistory
    else:
        print(f'Error in list_msg(). Room with roomCode [{roomCode}] does not exist.')
    return None

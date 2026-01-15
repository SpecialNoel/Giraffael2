# list_op.py

from server_only.mongodb_related.msg_ops.general_op import roomCode_to_roomID
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from bson import ObjectId

# List out all messages sent over this room
def list_msg_history(roomCode):
    roomID = roomCode_to_roomID(roomCode)

    if roomID:
        print(f'Msg history stored in room with roomCode [{roomCode}]:')
        room = rooms_collection.find_one(
            {'_id': ObjectId(roomID)}
        )
        msgMetadatas = room['msgList']
        for msgMetadata in msgMetadatas:
            print(f'[{msgMetadata['senderName']}]: [{msgMetadata['message']}]')
    else:
        print(f'Error in list_msg(). Room with roomCode [{roomCode}] does not exist.')
    return

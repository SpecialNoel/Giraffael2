# delete_op.py

from server_only.mongodb_related.file_ops.delete_op import delete_all_files
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from server_only.mongodb_related.msg_ops.general_op import roomCode_to_roomID
from bson import ObjectId
from bson.errors import InvalidId

# Delete a room in the DB (based on ObjectID of the room)
def delete_room(roomCode):
    roomID = roomCode_to_roomID(roomCode)
    try:
        room = rooms_collection.find_one(
            {'_id': ObjectId(roomID)}
        )
    except InvalidId:
        print(f'Error in upload_file(). roomID [{roomID}] is invalid.')
        return -1
    
    # Delete all files existed in that room first
    delete_all_files(roomID)
    # Delete the room in database
    rooms_collection.delete_one({'_id': ObjectId(roomID)})
    print(f'Successfully deleted room with roomID [{roomID}].')
    return

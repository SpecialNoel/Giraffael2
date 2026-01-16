# delete_op.py

from server_only.mongodb_related.file_ops.delete_op import delete_all_files
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from bson import ObjectId
from bson.errors import InvalidId

# Delete a room in the DB (based on ObjectID of the room)
def delete_room(room_code):
    room_id = room_code_to_room_id(room_code)
    try:
        room = rooms_collection.find_one(
            {'_id': ObjectId(room_id)}
        )
    except InvalidId:
        print(f'Error in upload_file(). room_id [{room_id}] is invalid.')
        return -1
    
    # Delete all files existed in that room first
    delete_all_files(room_id)
    # Delete the room in database
    rooms_collection.delete_one({'_id': ObjectId(room_id)})
    print(f'Successfully deleted room with room_id [{room_id}].')
    return

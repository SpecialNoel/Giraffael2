# delete_op.py

from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from server_only.mongodb_related.mongodb_initiator import rooms_collection, gfs
from bson import ObjectId
from bson.errors import InvalidId

# Delete a file in a room
def delete_file(file_id, room_code):
    try:
        file = gfs.find_one({'_id': ObjectId(file_id)})
        if not file:
            print(f'Error in delete_file(). File with file_id [{file_id}] does not exist in database.')
            return
    except InvalidId:
        print(f'Error in delete_file(). file_id [{file_id}] is invalid.')
        
    room_id = room_code_to_room_id(room_code)
        
    # Test if given room_id is in invalid format
    try:
        room = rooms_collection.find_one(
            {'_id': ObjectId(room_id)}
        )
    except InvalidId:
        print(f'Error in delete_file(). room_id [{room_id}] is invalid.')
        return
    
    if file.metadata['room_id'] != room_id:
        print(f'Error in delete_file(). File with file_id [{file_id}] does not exist in room [{room_id}].')
        return 
    
    # Delete the file, indicated by the file_id, from the database
    gfs.delete(ObjectId(file_id))
    # Remove the filename, indicated by the file_id, from 'file_list' of this room    
    rooms_collection.update_one(
        {'_id': ObjectId(room_id)},
        {'$pull': {'file_list': {'file_id': ObjectId(file_id)}}}
    )
    print(f'Successfully deleted file with file_id [{file_id}] in room [{room_id}].')
    return

# Delete all files in a room
def delete_all_files(room_id):
    # Use room_id to get all file_ids of the room, then use the file_ids to delete all files
    try:
        files = gfs.find({'metadata.room_id': room_id})
    except InvalidId:
        print(f'Error in delete_all_files(). room_id [{room_id}] is invalid')
        return
    
    if not files.alive:
        print(f'There are no existing files in room [{room_id}].')
        return
    for file in files:
        print(f'FileID to be deleted: [{file._id}]')
        delete_file(file._id, room_id)
    print(f'Successfully deleted all files from room [{room_id}].')
    return

# delete_op.py

from src.server.app.db.mongo.msg_ops.general_op import room_code_exists_in_collection
from src.server.app.db.mongo.file_ops.delete_op import delete_all_files
from src.server.app.db.mongo.mongodb_initiator import rooms_collection

# Delete a room in the DB (based on ObjectID of the room)
def delete_room(room_code):
    if not room_code_exists_in_collection(room_code):
        print(f'Error in upload_file(). Room [{room_code}] does not exist.')
        return -1
    
    # Delete all files existed in that room first
    delete_all_files(room_code)
    # Delete the room in database
    rooms_collection.delete_one({'roomCode': room_code})
    print(f'Successfully deleted room [{room_code}].')
    return

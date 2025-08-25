# delete_op.py

from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.database.file_ops.delete_op import delete_all_files
from v3src.server.database.mongodb_initiator import rooms_collection

# Delete a room in the DB (based on ObjectID of the room)
def delete_room(roomCode):
    if not room_code_exists_in_collection(roomCode):
        print(f'Error in upload_file(). Room code [{roomCode}] is invalid.')
        return -1
    
    # Delete all files existed in that room first
    delete_all_files(roomCode)
    # Delete the room in database
    rooms_collection.delete_one({'roomCode': roomCode})
    print(f'Successfully deleted room with room code [{roomCode}].')
    return

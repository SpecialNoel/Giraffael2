# delete_op.py

from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.database.mongodb_initiator import rooms_collection

def delete_client_from_list(address, roomCode):
    if room_code_exists_in_collection(roomCode):
        rooms_collection.update_one(
            {'roomCode': roomCode},
            {'$pull': {'clientList': {'address': address}}}
        )
        print(f'Successfully deleted client with address [{address}] from the clientList of room with roomCode [{roomCode}].')
    else: 
        print(f'Error in delete_client_to_list(). Room with roomCode [{roomCode}] does not exist.')
    return

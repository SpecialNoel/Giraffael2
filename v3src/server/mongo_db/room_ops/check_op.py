# check_op.py

from v3src.server.mongo_db.msg_ops.general_op import room_code_exists_in_collection

# Check whether room with given room code exist in MongoDB
def check_room_existence(roomCode):
    if not room_code_exists_in_collection(roomCode):
        print(f'Room [{roomCode}] does not exist in MongoDB.')
        return False
    print(f'Room [{roomCode}] exists in MongoDB.')
    return True

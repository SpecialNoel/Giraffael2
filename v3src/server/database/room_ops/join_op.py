# join_op.py

from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection

def join_room(roomCode):
    # Check if the given roomCode is indeed corresponding to a room stored in database
    if not room_code_exists_in_collection(roomCode):
        print(f'Error in join_room(). Room with roomCode [{roomCode}] does not exist in database.')
        return False
    return True

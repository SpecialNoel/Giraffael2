# join_op.py

from v3src.server.database.msg_ops.general_op import roomCode_to_roomID

def join_room(roomCode):
    # Check if the given roomCode is indeed corresponding to a room stored in database
    if roomCode_to_roomID(roomCode) == None:
        print(f'Error in join_room(). Room with roomCode [{roomCode}] does not exist in database.')
        return False
    return True

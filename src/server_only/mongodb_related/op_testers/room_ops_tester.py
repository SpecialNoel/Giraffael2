# room_ops_tester.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))

from room_ops.create_op import create_room
from room_ops.delete_op import delete_room

if __name__=='__main__':  
    roomCode = 'f9wa8rq9fqvg0qj'
    roomID = '681e9d269581da6a87579f37'
    
    #create_room(roomCode)
    #delete_room(roomID)
    
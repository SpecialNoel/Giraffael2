# download_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from mongodb_initiator import rooms_collection, gfs
from file_ops.general_op import roomCode_to_roomID
src_folder = Path(__file__).resolve().parents[3] # grandparent level
sys.path.append(str(src_folder))

import os
from bson import ObjectId
from bson.errors import InvalidId
from gridfs.errors import NoFile

# Download file from a room
# Note: the only intended way to use download_file() is to query target file from database 
#       to server_only/handle_requests/file_buffer_folder, then the server can send that file
#       to the client. Client download request has to be done this way given that server
#       has to first send the metadata of the file to the client, before the whole file can
#       be sent to the client.
def download_file(fileID, roomCode, savedir):
    try: 
        file = gfs.get(ObjectId(fileID))
    except InvalidId:
        print(f'Error in download_file(). FileID [{fileID}] is invalid.')
        return
    except NoFile: 
        print(f'Error in download_file(). File with fileID [{fileID}] does not exist in database.')
        return
    
    roomID = roomCode_to_roomID(roomCode)
    
    # Test if given roomID is in invalid format
    try:
        room = rooms_collection.find_one(
            {'_id': ObjectId(roomID)}
        )
    except InvalidId:
        print(f'Error in download_file(). roomID [{roomID}] is invalid.')
        return
    
    # Test if the file is in database, but not in the given room 
    if file.metadata['roomID'] != roomID:
        print(f'Error in download_file(). File with fileID [{fileID}] does not exist in room [{roomID}].')
        return 
    
    # Start downloading the file
    filename = file.filename 
    # Note that savepath could potentially be colliding with other files in local file_buffer_folder
    savepath = os.path.join(savedir, filename)
    with open(savepath, 'wb') as f:
        f.write(file.read())
    print(f'Downloaded file with fileID [{fileID}] from room [{roomID}], stored at [{savepath}].')
    return savepath
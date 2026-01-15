# download_op.py

import os
from server_only.mongodb_related.msg_ops.general_op import roomCode_to_roomID
from server_only.mongodb_related.mongodb_initiator import rooms_collection, gfs
from general.file_transmission import get_filepath_without_duplication
from bson import ObjectId
from bson.errors import InvalidId
from gridfs.errors import NoFile

# Download file from a room
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
    savepath = os.path.join(savedir, filename)
    # Add a unique postfix to the filename of the savepath to avoid duplicated filename inside user-end folder.
    savepath = get_filepath_without_duplication(savepath)
    with open(savepath, 'wb') as f:
        f.write(file.read())
    print(f'Downloaded file with fileID [{fileID}] from room [{roomID}], stored at [{savepath}].')
    return
# download_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from mongodb_initiator import rooms_collection, gfs
src_folder = Path(__file__).resolve().parents[3] # grandparent level
sys.path.append(str(src_folder))
from general.file_transmission import get_filepath_without_duplication

import os
from bson import ObjectId
from bson.errors import InvalidId
from gridfs.errors import NoFile


# Download file from a room
def download_file(fileID, roomID, savedir):
    try: 
        file = gfs.get(ObjectId(fileID))
    except InvalidId:
        print(f'Error in download_file(). FileID [{fileID}] is invalid.')
        return
    except NoFile: 
        print(f'Error in download_file(). File with fileID [{fileID}] does not exist in database.')
        return
    
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
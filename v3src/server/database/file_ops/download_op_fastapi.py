# download_op_fastapi.py

import io
from bson import ObjectId
from bson.errors import InvalidId
from fastapi.responses import StreamingResponse
from gridfs.errors import NoFile
from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.database.mongodb_initiator import rooms_collection, gfs

# Download file from a room
# Note: the only intended way to use download_file() is to query target file from database 
#       to server_only/handle_requests/file_buffer_folder, then the server can send that file
#       to the client. Client download request has to be done this way given that server
#       has to first send the metadata of the file to the client, before the whole file can
#       be sent to the client.
def download_file_with_fastapi(roomCode, fileID):
    try: 
        file = gfs.get(ObjectId(fileID))
    except InvalidId:
        print(f'Error in download_file(). FileID [{fileID}] is invalid.')
        return
    except NoFile: 
        print(f'Error in download_file(). File with fileID [{fileID}] does not exist in database.')
        return

    # Test if given room code is in invalid format
    if not room_code_exists_in_collection(roomCode):
        print(f'Error in download_file(). Room code [{roomCode}] is invalid.')
        return
    
    # Test if the file is in database, but not in the given room 
    if file.metadata['roomCode'] != roomCode:
        print(f'Error in download_file(). File with fileID [{fileID}] does not exist in room [{roomCode}].')
        return 
    print(f'File {file.filename} belongs to room {roomCode}, proceeding with download.')
    
    fileData = file.read()
    filename = file.filename or 'downloaded_file'
    return StreamingResponse(
        io.BytesIO(fileData),
        media_type='application/octet-stream',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

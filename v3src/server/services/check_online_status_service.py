# check_online_status_service.py

from v3src.server.mongo_db.file_ops.list_op import get_fileID
from v3src.server.mongo_db.file_ops.upload_op_fastapi import upload_file_with_fastapi
from v3src.server.mongo_db.file_ops.download_op_fastapi import download_file_with_fastapi

def upload_file_service(roomCode: str, file: UploadFile = File(...)):
    result = upload_file_with_fastapi(roomCode, file)
    return {'status': 'succeeded'} if result == -1 else {'status': 'failed'}

def download_file_service(roomCode: str, filename: str):
    fileID = get_fileID(filename, roomCode)
    if fileID == None:
        print(f'Error in download_file(): {fileID} is invalid.')
        return None

    return download_file_with_fastapi(roomCode, fileID)

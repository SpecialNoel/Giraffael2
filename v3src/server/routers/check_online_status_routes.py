# check_online_status_routes.py

from fastapi import APIRouter
from v3src.server.services.file_service import upload_file_service, download_file_service

router = APIRouter()

# FastAPI endpoint for handling a 'upload' request from a client
@router.post('/upload/{roomCode}')
def upload_file(roomCode: str, file: UploadFile = File(...)):
    return upload_file_service(roomCode, file)

# FastAPI endpoint for handling a 'download' request from a client
@router.get('/download/{roomCode}/{filename}')
def download_file(roomCode: str, filename: str):
    return download_file_service(roomCode, filename)

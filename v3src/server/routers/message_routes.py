# message_routes.py

from fastapi import APIRouter
from v3src.server.schemas.definitions import EncryptedMsg
from v3src.server.services.message_service import send_msg, fetch_msg

router = APIRouter()
msgList = {}

# FastAPI endpoint for handling a 'send' request from a sender client
@router.post('/send')
def send_message(msg: EncryptedMsg):
    return send_msg(msg, msgList)

# FastAPI endpoint for handling a 'fetch' request from a receiver client
@router.get('/fetch/{recipientID}')
def fetch_message(recipientID: str):
    return fetch_msg(recipientID, msgList)

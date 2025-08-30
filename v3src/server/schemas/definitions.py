# definitions.py

from pydantic import BaseModel

class EncryptedMsg(BaseModel):
    typeOfMsg: str
    senderID: str
    recipientID: str
    cipherText: str
    nonce: str
    
class RoomRequest(BaseModel):
    room_code: str
    username: str

# definitions.py

from pydantic import BaseModel

class EncryptedMsg(BaseModel):
    typeOfMsg: str
    senderID: str
    recipientID: str
    cipherText: str
    nonce: str

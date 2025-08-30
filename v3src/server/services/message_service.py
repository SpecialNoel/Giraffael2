# message_service.py

from v3src.server.schemas.definitions import EncryptedMsg

def send_msg(msg: EncryptedMsg, msgList: dict):
    try:
        if msg.recipientID not in msgList:
            msgList[msg.recipientID] = []

        msgList[msg.recipientID].append(msg.model_dump())
        print(f'Stored for {msg.recipientID}: {msgList[msg.recipientID]}')
        return {'status': 'succeeded'}
    except:
        print(f'Failed to store for {msg.recipientID}: {msgList[msg.recipientID]}')
        return {'status': 'failed'}

def fetch_msg(recipientID: str, msgList: dict):
    try:
        msgs = msgList.pop(recipientID, [])
        return {'messages': msgs}
    except:
        return {'messages': None}
    
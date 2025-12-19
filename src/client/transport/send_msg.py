# sned_msg.py

import json
import requests

async def send_chat_message(room_code, uuid, user_input, websocket):
    msg = {
        'type': 'chat',
        'room_code': room_code,
        'uuid': uuid,
        'payload': user_input,
    }
    await websocket.send(json.dumps(msg))
    print('Sent message to server. ')
    return

async def send_create_room_request(base_http_uri, username, room_code):
    print('Sending the create room request to server.')
    
    room_creation_uri = base_http_uri + '/room/create'
    data = {'room_code': room_code, 'username': username}
    
    response = requests.post(room_creation_uri, json=data)
    print(f'Response status code: {response.status_code}')
    print(f'Received status from server: {response.json()}')
    return

async def send_disconnect_request(websocket):
    await websocket.close()
    print('Disconnected from server. Exited')
    return
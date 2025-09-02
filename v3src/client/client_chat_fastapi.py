# client_chat_fastapi.py

# Note: Add one of the options to the command below: [send, recv, upload, download]
# python -m v3src.client.client_chat_fastapi

import base64
import os
import json
import asyncio
import requests
import websockets
import tkinter as tk
from tkinter import filedialog
from v3src.client.encryption import encrypt, decrypt

# Helper functions
def get_file_extension(filename):
    # Returns the extension of a file, including dot.
    # Example: .txt, .pdf, .png, etc..
    return os.path.splitext(filename)[1]
def get_file_dir_path(filepath):
    return os.path.dirname(filepath)

# --------------------------------------------------------------------------------
# New Key functions


# For create-room and delete-room requests, client should use FastAPI endpoint (HTTP POST).
async def send_create_room_request(base_http_uri, base_ws_uri, username, room_code, VALID_ACTIONS):
    print('Sending the create room request to server.')
    
    room_creation_uri = base_http_uri + '/room/create'
    data = {'room_code': room_code, 'username': username}
    
    response = requests.post(room_creation_uri, json=data)
    print(f'Response status code: {response.status_code}')
    print(f'Received status from server: {response.json()}')

    # If received 'succeeded' status, send WebSocket request to server to be connected with server    
    if response.json()['status'] == 'succeeded':
        uuid = response.json()['uuid']
        await send_connect_request(base_ws_uri, uuid, username, room_code, VALID_ACTIONS)
    return

async def send_disconnect_request(websocket):
    await websocket.close()
    print('Disconnected from server. Exited')
    return

# For create-room and delete-room requests, client should use FastAPI endpoint (HTTP POST).
async def send_delete_room_request(room_code):
    print(f'Deleted room [{room_code}].')
    return

async def send_join_room_request(room_code):
    print(f'Joined room [{room_code}].')
    return

async def send_leave_room_request(room_code):
    print(f'Left room [{room_code}].')
    return

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

# Used to test service side connection with Connection Manager + Redis
async def send_connect_request(base_ws_uri, uuid, username, room_code, VALID_ACTIONS):        
    uri = base_ws_uri + f'?room_code={room_code}&uuid={uuid}&username={username}'
    print(f'uri: [{uri}].')
    
    # Client connects to server via WebSocket endpoint
    async with websockets.connect(uri) as websocket:        
        msg = await websocket.recv()
        data = json.loads(msg)
        print(f'Response from server: {data}')
        
        if data['status'] != 'succeeded':
            print('Failed to connect to server.')
            return
        print('Successfully connected to server.')
        
        # Start receiving heartbeat in the background
        receiver_thread = asyncio.create_task(receive_msg(websocket))
        sender_thread = asyncio.create_task(user_input_loop(websocket, room_code, uuid, VALID_ACTIONS))
        
        # Wait until either finishes (either disconnects or error occurs)
        done, pending = await asyncio.wait(
            [receiver_thread, sender_thread],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel the unfinished tasks before stopping the client loop
        for task in pending:
            task.cancel()
        print('Client loop ended.')
    return

async def receive_msg(websocket):
    try:
        async for raw_msg in websocket:
            msg = json.loads(raw_msg)
            
            if msg.get('type') == 'ping':
                # Handle ping signal by sending back a pong to server 
                await websocket.send(json.dumps({'type': 'pong'}))
                print('Sent pong to server')
            else:
                # Handle other messages
                await handle_incoming_message(msg)
    except websockets.ConnectionClosed:
        print('Connection closed by server.')
    except Exception as e:
        print(f'Unexpected error in recv_heartbeat(): {e}.')
        
async def user_input_loop(websocket, room_code, uuid, VALID_ACTIONS):
    try: 
        print(f'Please choose from the available actions, or start typing message to the room.')
        print(f'Available actions: {VALID_ACTIONS}.')
        
        while True:
            # Run input() in a separate thread to get user input
            user_input = await asyncio.to_thread(input, '> ')
            user_input = user_input.strip()
            
            # Handle user input
            if user_input == 'disconnect':
                await send_disconnect_request(websocket)
                break
            elif user_input == 'delete':
                await send_delete_room_request(room_code)
            elif user_input == 'join':
                await send_join_room_request(room_code)
            elif user_input == 'leave':
                await send_leave_room_request(room_code)
            else:
                await send_chat_message(room_code, uuid, user_input, websocket)
                
    except Exception as e:
        print(f'Error in user_input_loop(): {e}.')

async def handle_incoming_message(msg):
    print('In handle_incoming_message().')
    print(f'Received unexpected msg in recv_heartbeat(): [{msg}]')
    return

# --------------------------------------------------------------------------------
# Old Key functions

# FastAPI logic for creating and joining a room with given room code
def create_and_join_room_with_room_code(uri, roomCode):
    # Client connects to the server via WebSocket
    response = requests.post(uri+'ws/')
    
    # Client then proceeds to room creation 
    response = requests.post(uri+'room/create/'+roomCode)
    print(f'Response status code: {response.status_code}')
    print(f'Received status from server: {response.json()}')
    if response.json().get('status') == 'succeeded':
        print(f'Created and joined room [{roomCode}].\n')
    else:
        print(f'Failed to create room [{roomCode}.]\n')
    return

# FastAPI logic for joining a room with given room code
def join_room_with_room_code(uri, roomCode):
    response = requests.post(uri+'room/join/'+roomCode)
    print(f'Response status code: {response.status_code}')
    print(f'Received status from server: {response.json()}')
    if response.json().get('status') == 'succeeded':
        print(f'Joined room [{roomCode}].\n')
    else:
        print(f'Failed to join room [{roomCode}.]\n')
    return

# FastAPI logic for sending a message to a target client
def send(uri, senderID, recipientID, key, plainText):
    def get_payload(senderID, recipientID, key, plainText):
        encryptedText = encrypt(key, plainText)
        # base64.b64encode() turns binary bytes into base64 bytes, and
        # decoding base64 bytes gives us an UTF-8 string, the supported format in JSON.
        cipherTextStr = base64.b64encode(encryptedText['cipherText']).decode()
        nonceStr = base64.b64encode(encryptedText['nonce']).decode()
        payload = {
            'typeOfMsg': 'message',
            'senderID': senderID,
            'recipientID': recipientID,
            'cipherText': cipherTextStr,
            'nonce': nonceStr
        }
        return payload
    
    payload = get_payload(senderID, recipientID, key, plainText)
    response = requests.post(uri+'send', json=payload)
    print(f'Received status from server: {response.json()}')
    if response.json().get('status') == 'succeeded':
        print(f'Sent message [{plainText.decode()}] to [{recipientID}].')
    return

# FastAPI logic for fetching a message as a receiver client
def recv(uri, recipientID, key):
    response = requests.get(uri+'fetch/'+recipientID)
    print(f'Response status code: {response.status_code}')
    try:
        data = response.json()
        messages = data.get('messages', [])
        if messages == []: 
            print('No new message fetched.')
        else:
            print('Fetched the following new messages:')
    except ValueError:
        print(f'Invalid JSON: {response.text}')
        messages = []
    for message in messages:
        senderID = message['senderID']
        cipherText = base64.b64decode(message['cipherText'])
        nonce = base64.b64decode(message['nonce'])
        plainText = decrypt(key, cipherText, nonce).decode()
        print(f'From [{senderID}]: {plainText}')
    return

# FastAPI logic for uploading a file with given file content and room code
def upload(uri, roomCode, filename):
    def ask_file_location(filename, fileExtension):
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(defaultextension=fileExtension, initialfile=filename)
        return filepath
    
    fileExtension = get_file_extension(filename)
    filepath = ask_file_location(filename, fileExtension)
    
    if os.path.isfile(filepath):
        print(f'✅ File [{filename}] exists on user local machine.')
    else:
        print(f'❌ File [{filename}] does not exist on user local machine.')
    
    with open(filepath, 'rb') as f:
        files = {'file': (filename, f)}
        response = requests.post(uri+'upload/'+roomCode, files=files)
        print(f'Response status code: {response.status_code}')
    return 

# FastAPI logic for downloading a file with given filename and room code
def download(uri, roomCode, filename, chunkSize):
    def ask_file_save_location(filename, fileExtension):
        # Additional arguments for filedialog.asksaveasfilename();
        #   provides default file extensions to users for selection.
        fileTypes = [('Text files', '*.txt'),
                     ('PDF files', '*.pdf'),
                     ('JPG files', '*.jpg'),
                     ('JPEG files', '*.jpeg'),
                     ('PNG files', '*.png'),
                     ('All files', '*.*')]
        
        root = tk.Tk()
        root.withdraw() # This hides the main window of Tk
        savePath = filedialog.asksaveasfilename(defaultextension=fileExtension, 
                                                initialfile=filename)
        return savePath
    
    # Setting 'stream' to True allows the client to download the file without loading it into memory
    response = requests.get(uri+'download/'+roomCode+'/'+filename, stream=True)
    print(f'Response status code: {response.status_code}')
    
    fileExtension = get_file_extension(filename)
    print('file ext:', fileExtension)
    savePath = ask_file_save_location(filename, fileExtension)
    try: 
        with open(savePath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunkSize):
                f.write(chunk)
        fileDirPath = get_file_dir_path(savePath)
        print(f'✅ File [{filename}] downloaded successfully. It is stored in [{fileDirPath}].')
    except Exception as e:
        print(f'❌ Failed to download file [{filename}].')
        print(f'Failed reason: {e}.')
    return

if __name__=='__main__':
    CHUNK_SIZE = 1024
    uri = 'http://10.0.0.33:5001/'
    senderID = 'Dodo'
    recipientID = 'Fish'
    key = b'1234567890abcdef12345678'
    plainText = b'This is a plain text message.'
    roomCode = 'fWpO003k8z6'
    filename = 'cc.jpeg'
    
    
    VALID_ACTIONS = {'create', 'delete', 'join', 'leave', 'disconnect'}
    base_http_uri = 'http://10.0.0.33:5001/'
    base_ws_uri = 'ws://10.0.0.33:5001/ws'
    username = 'dodo'
    room_code = 'fWpO003k8b2'
    asyncio.run(send_create_room_request(base_http_uri, base_ws_uri, username, room_code, VALID_ACTIONS))
    
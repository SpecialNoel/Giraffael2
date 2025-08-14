# client_chat_fastapi.py

# Note: replace 'arg' below with one of the action: [send, recv, upload, download]
# python -m v3src.client.client_chat_fastapi arg

import base64
import os
import requests
import sys
import tkinter as tk
from tkinter import filedialog
from v3src.client.encryption import encrypt, decrypt

def get_file_extension(filename):
    # Returns the extension of a file, including dot.
    # Example: .txt, .pdf, .png, etc..
    return os.path.splitext(filename)[1]

def get_file_dir_path(filepath):
    return os.path.dirname(filepath)

# FastAPI logic for creating and joining a room with given room code
def create_room_with_room_code(uri, roomCode):
    response = requests.post(uri+'/room/create/'+roomCode)
    print(f'Response status code: {response.status_code}')
    print(f'Received status from server: {response.json()}')
    if response.json().get('status') == 'success':
        print(f'Created and joined room [{roomCode}].\n')
    else:
        print(f'Failed to create room [{roomCode}.]\n')
    return

# FastAPI logic for joining a room with given room code
def join_room_with_room_code(uri, roomCode):
    response = requests.post(uri+'/room/join/'+roomCode)
    print(f'Response status code: {response.status_code}')
    print(f'Received status from server: {response.json()}')
    if response.json().get('status') == 'success':
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
    if response.json().get('status') == 'success':
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
    roomCode = 'fWpO003k8z5'
    filename = 'cc.jpeg'
    
    choice = sys.argv[1]
    
    create_room_with_room_code(uri, roomCode)
    
    if choice == 'send':
        send(uri, senderID, recipientID, key, plainText)
    elif choice == 'recv':
        recv(uri, recipientID, key)
    elif choice == 'upload':
        upload(uri, roomCode, filename)
    elif choice == 'download':
        download(uri, roomCode, filename, CHUNK_SIZE)
    else:
        print('Invalid argument passed when executing client_chat_fastapi.py')

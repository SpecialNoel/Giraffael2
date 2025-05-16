# handle_username.py

from client_only.client_core.send_to_server import send_username

def handle_username(client, chunkSize):
# Try sending client username to server
    msg, response = send_username(client, chunkSize)
    while response != 'VALID_USERNAME':
        print(f'msg: [{msg}], response from server: [{response}]')
        msg, response = send_username(client, chunkSize)
    return
        
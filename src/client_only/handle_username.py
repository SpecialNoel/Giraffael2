# handle_username.py

from send_to_server import send_username

def handle_username(client, msgContentSize):
# Try sending client username to server
    msg, response = send_username(client, msgContentSize)
    while response != 'VALID_USERNAME':
        print(f'msg: [{msg}], response from server: [{response}]')
        msg, response = send_username(client, msgContentSize)
        
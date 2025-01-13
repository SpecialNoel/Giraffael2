# file_transmission.py

import os
from pathlib import Path

# Functions here are used by clients or server to transfer 
#   different kinds of files (.jpg, .pdf, .txt, .csv, etc.).


# Used by the sender to get the filepath of a file from the current directory
def get_filepath(filename):
    return Path.cwd() / filename


# Used by the sender to check if the file exists or not
def check_if_file_exists(filepath):
    return os.path.isfile(filepath)


# Used by the sender to create the associate metadata of the file
# The metadata will be sent to the recipient to receive the original file
def create_metadata(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    return filename, filesize


# Used by the sender to send the metadata of a file to the recipient
def send_metadata(filename, filesize, socket):
    msg = f'{filename}|{filesize}'
    socket.send(msg.encode())
    return


# Used by the recipient to receive the metadata of a file from the sender
def recv_metadata(socket):
    msg = socket.recv(1024)
    if not msg:
        return None, None
    filename, filesize = msg.split('|')
    return filename, filesize


# Used by the sender to send the file to the recipient
def send_file(filepath, socket, chunk_size):
    with open(filepath, 'rb') as file:
        while chunk := file.read(chunk_size):
            socket.send(chunk)
    return


# Used by the recipient to receive the file from the sender
# Received content will be stored in the "received_files" folder
#   with the same filename as the received filename.
def recv_file(filename, filesize, socket, chunk_size):
    print(f'Received file with filename: {filename}')
    filepath_prefix = 'received_files/'
    filename = filepath_prefix + filename
    print(f'Stored in filepath: {filename}')
    
    with open(filename, 'wb') as file:
        received_len = 0
        while received_len < filesize:
            data = socket.recv(chunk_size)
            if not data:
                break
            file.write(data)
            received_len += len(data)
    return
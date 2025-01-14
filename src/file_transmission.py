# file_transmission.py

import os
from pathlib import Path

'''
Functions here are used by clients or server to transfer 
  different kinds of files (.jpg, .pdf, .txt, .csv, etc.).
'''


def get_filepath(filename):
    '''
    Used by the sender to get the filepath of a file from the current directory.

    @param filename: the string name of the file
    @return: filepath
    '''
    return Path.cwd() / filename


def check_if_file_exists(filepath):
    '''
    Used by the sender to check if the file exists or not.

    @param filepath: the filepath of the file
    @return: True if the filepath is a file; False otherwise 
    '''
    return os.path.isfile(filepath)


def create_metadata(filepath):
    '''
    Used by the sender to create the associate metadata of the file.
    The metadata will be sent to the recipient before receiving 
    the original file.

    @param filepath: the filepath of the file
    @return: filename, filesize
    '''
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    return filename, filesize


def send_metadata(filename, filesize, socket):
    '''
    Used by the sender to send the metadata of a file to the recipient.

    @param filename: the string name of the file
    @param filesize: the size of the file
    @param socket: the socket used to send the metadata; the sender socket
    @return: None
    '''
    msg = f'{filename}|{filesize}'
    socket.send(msg.encode())
    return


def recv_metadata(socket):
    '''
    Used by the recipient to receive the metadata of a file from the sender.
    
    @param socket: the socket used to receive the metadata; the receiver socket
    @return: filename, filesize
    '''
    msg = socket.recv(1024)
    if not msg:
        return None, None
    filename, filesize = msg.split('|')
    return filename, filesize


def send_file(filepath, socket, chunk_size):
    '''
    Used by the sender to send the file to the recipient.
    
    @param filepath: the filepath of the file
    @param socket: the socket used to send the file; the sender socket
    @chunk_size: number of bytes to send to the recipient each time
    @return: None
    '''
    with open(filepath, 'rb') as file:
        while chunk := file.read(chunk_size):
            socket.send(chunk)
    return


def recv_file(filename, filesize, socket, chunk_size):
    '''
    Used by the recipient to receive the file from the sender.
    Received content will be stored in the "received_files" folder
      with the same filename as the received filename.
    
    @param filename: the string name of the file
    @param filesize: the size of the file
    @param socket: the socket used to receive the file; the receiver socket
    @chunk_size: number of bytes to receive from the sender each time
    @return: None
    '''
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
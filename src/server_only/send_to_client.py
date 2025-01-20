# send_to_client.py

from general.file_transmission import (get_filepath, check_if_file_exists,
                                      create_metadata, send_file)
from general.message import add_prefix

def send_file_to_client(client, filename, msgContentSize):
    # Check if requested file exists on server
    # If does, inform client by sending ('1'), then send metadata
    # If not, inform client by sending ('-1'), then return
    
    
    # Create filepath from filename
    filepath = get_filepath(filename)
    if not check_if_file_exists(filepath):
        return
    
    # Create and send metadata to client
    filename, filesize = create_metadata(filepath)
    msg = f'{filename}|{filesize}'
    msgWithPrefix = add_prefix(msg.encode(), 1)
    client.send(msgWithPrefix)        
    
    # Send the whole file to client
    send_file(filepath, filename, client, 
             msgContentSize, client.getpeername())
    return
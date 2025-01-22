# send_to_client.py

from general.file_transmission import (create_metadata, display_rule,
                                      send_file, send_metadata)

def send_file_to_client(client, filepath, msgContentSize):
    # Create and send metadata to client
    filename, filesize = create_metadata(filepath)
    send_metadata(client, filename, filesize)
   
    # Send the whole file to client
    send_file(filepath, filename, client, 
             msgContentSize, client.getpeername())
    
    display_rule()
    return

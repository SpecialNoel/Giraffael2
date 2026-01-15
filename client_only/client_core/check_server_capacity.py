# check_server_capacity.py

from general.message import recv_decoded_content

def check_server_capacity(client, chunkSize):
    # When trying to connect to server, if server sent '-1', it means that
    #  server has reached the max number of clients.
    # Thus the connection should fail.
    
    msg = recv_decoded_content(client, chunkSize)
    print(f'Init msg from server: [{msg}].')
    
    if msg == '-1':
        print('Connection refused by server: max client count reached.')
    else:
        print('Connected to server successfully!')
    
    return msg != '-1'

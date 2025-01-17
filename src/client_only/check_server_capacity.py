# check_server_capacity.py


from general.message import rstrip_message
                             

def check_server_capacity(client, msgContentSize):
    # When trying to connect to server, if server sent '-1', it means that
    #  server has reached the max number of clients.
    # Thus the connection should fail.
    msg = rstrip_message(client.recv(msgContentSize)).decode()
    print(f'Init msg from server: {msg}.')
    
    if msg == '-1':
        print('Connection refused by server: max client count reached.')
    else:
        print('Connected to server successfully!')
    
    return msg != '-1'
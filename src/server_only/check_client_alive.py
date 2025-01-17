# check_client_alive.py

def check_client_alive(client):
    try:
        # If able to send an empty message to client without errors,
        #   it means that the client is still connected.
        client.send(b'')
        return True
    except (BrokenPipeError, 
            ConnectionResetError, 
            ConnectionAbortedError) as e:
        # Otherwise, client has already disconnected.
        print(f'Error: {e}. ',
                f'Connection with {client} is no longer alive.')
        return False
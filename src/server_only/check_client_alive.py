# check_client_alive.py

def check_client_alive(client):
    try:
        # If able to send an empty message to client without errors,
        #   it means that the client is still connected.
        # Update: changed this to b'\x02HEART' since TLS does not allow
        #         the transmission of empty message. Need to handle this
        #         message on client side properly.
        client.send(b'\x02HEART')
        return True
    except (BrokenPipeError, 
            ConnectionResetError, 
            ConnectionAbortedError) as e:
        # Otherwise, client has already disconnected.
        print(f'Error: [{e}]. ',
              f'Connection with [{client}] is no longer alive.')
        return False

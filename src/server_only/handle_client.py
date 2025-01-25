# handle_client.py

from general.message import get_prefix_and_content
from server_only.handle_download_request import handle_download_request
from server_only.handle_normal_msg import handle_normal_msg
from server_only.remove_client import handle_disconnect_request
from server_only.handle_upload_request import handle_upload_request
from threading import Thread, Event

def handle_one_client(shutdownEvent, clientObj, clients, chunkSize,
                      rooms, roomCodes, maxClientCount, maxFileSize, extList):
    client = clientObj.get_socket()
    address = clientObj.get_address()
    roomCode = clientObj.get_room_code()
    handleClientEvent = Event()
    try:
        while not shutdownEvent.is_set():
            try:
                if handleClientEvent.is_set():
                    break
                
                msg = client.recv(chunkSize) # 1025 bytes
                
                # Empty message -> client closed connection
                if not msg:
                    handle_disconnect_request(client, clients, address, 
                                              rooms, roomCode, roomCodes,
                                              maxClientCount, 
                                              handleClientEvent)
                    return
                
                t = Thread(target=handle_client_thread,
                        args=(client, msg, clients, address, rooms, 
                                roomCode, roomCodes, maxClientCount,
                                chunkSize, maxFileSize, extList, 
                                handleClientEvent,))
                t.daemon = False # thread ends when the main thread ends
                t.start()
            except (BrokenPipeError, 
                    ConnectionResetError, 
                    ConnectionAbortedError) as e:
                # Close connection with this client
                print(f'Error: [{e}]. ',
                      f'Removed [{address}] from client socket list.')
                handle_disconnect_request(client, clients, address, 
                                        rooms, roomCode, roomCodes,
                                        maxClientCount, handleClientEvent)            
                break
            except ValueError:
                print(f'Error: [{e}]. Invalid header received from [{address}]].')
                break
            except Exception as e:
                print(f'Error: [{e}]. Closing connection with [{address}].\n')
                client.close()
                handleClientEvent.set()
                break
    finally:
        client.close()
        print(f'In finally: Connection with [{address}] closed.')
    return

def handle_client_thread(client, msg, clients, address, rooms, 
                         roomCode, roomCodes, maxClientCount,
                         chunkSize, maxFileSize, extList, handleClientEvent):
    
    try:
        typePrefix, msgContent = get_prefix_and_content(msg)
        prefix = int.from_bytes(typePrefix, byteorder='big')
        
        print(f'msg: [{msg}]')
        print(f'Type Prefix: [{typePrefix}]')
        print(f'Content: [{msgContent}]')
        print(f'Prefix: [{prefix}]')
        
        match prefix:
            case 0: # Received operation message
                print('Received operation message.')
                print(f'msgContent:{msgContent}\n')
            case 1: # Received normal message
                handle_normal_msg(client, msgContent, clients, 
                                rooms, roomCode)
            case 2: # Received file-upload request
                handle_upload_request(client, address, 
                                    chunkSize, maxFileSize, extList)
            case 3: # Received file-download request
                handle_download_request(client, address, 
                                        msgContent, chunkSize, 
                                        maxFileSize, extList)
            case _: # Received invalid prefix
                print(f'Received invalid prefix: {typePrefix}.')
        return
    except ConnectionResetError as e:
        print(f'Error in handle_client_thread(): [{e}].')
        handleClientEvent.set()
        client.close()
        return

# message.py

'''
Functions here are used to argument messages transmitted
  between clients and server.

************************************************
* Note: all 'message' instances mentioned here * 
*       refer to bytes-object, not string.     *
************************************************
'''

def rstrip_message(msg):
    '''
    Used for removing the new line character at the end of the message.

    @param msg: a bytes-object
    @return: a copy of the message with trailing spaces 
             or new line chars removed
    '''
    return msg.rstrip()

def add_prefix(msg, typePrefix=0):
    '''
    Used to add a type prefix to the message to indicate its usage.
    Note that this only applies when the client is already inside a room.
    
    Type prefixes:
    0: Operation message  (room code, username, etc.)
    1: Normal message     (decode-able)
    2: File-upload        (not decode-able)
    3: File-download      (not decode-able)
    4: Display history    (msg/file)
    5: Clear history      (msg/file/all)

    @param msg: a bytes-object
    @param typePrefix: an integer
    @return: message with typePrefix appended to the front
    '''
    return (typePrefix.to_bytes(1, byteorder='big')) + msg

def get_prefix_and_content(msg):
    '''
    Used to obtain type prefix and message content of the message.

    @param msg: a bytes-object
    @return: typePrefix, messageContent
    '''
    typePrefix = msg[:1] # first char
    msgContent = msg[1:] # the rest chars, starting from the 2nd
    return typePrefix, msgContent

def recv_decoded_content(client, chunkSize):
    msg = client.recv(chunkSize)
    prefix, content = get_prefix_and_content(msg)
    return rstrip_message(content).decode()
    
def send_msg_with_prefix(client, msg, prefix):
    client.send(add_prefix(msg.encode(), prefix))
    return

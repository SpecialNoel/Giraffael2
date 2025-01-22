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

def add_prefix(msg, typePrefix):
    '''
    Used to add a type prefix to the message to indicate its usage.
    Note that this only applies when the client is already inside a room.
    
    Type prefixes:
    0: Normal message (exchanged in channel/chatroom; 
                       metadata is included here)
    1: File-upload   (not decode-able)
    2: File-download (not decode-able)
    
    Note that we don't take care of the room code nor the username here, since
      they were handled BEFORE the client enters/creates a room.
    * RoomCode       (exchanged during room code step)
    * Username       (exchanged during username step)

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
    
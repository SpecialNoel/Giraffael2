# message.py

'''
Functions here are used to argument messages transmitted
  between clients and server.

************************************************
* Note: all 'message' instances mentioned here * 
*       refer to bytes-object, not string.     *
************************************************
'''


def rstrip_message(message):
    '''
    Used for removing the new line character at the end of the message.

    @param message: a bytes-object
    @return: a copy of the message with trailing spaces or new line chars removed
    '''
    return message.rstrip()


def add_prefix_to_message(message, typePrefix):
    '''
    Used to add a type prefix to the message to indicate its usage.
    
    Type prefixes:
    0: Normal message (exchanged in channel/chatroom; metadata is included here)
    1: File content   (not decode-able)
    2: RoomCode       (exchanged during room code step)
    3: Username       (exchanged during username step)

    @param message: a bytes-object
    @param typePrefix: an integer
    @return: message with typePrefix appended to the front
    '''
    return (typePrefix.to_bytes(1, byteorder='big')).encode() + message


def separate_type_prefix_and_content_from_message(message):
    '''
    Used to obtain type prefix and message content of the message.

    @param message: a bytes-object
    @return: typePrefix, messageContent
    '''
    typePrefix = message[0] # first char
    messageContent = message[1:] # the rest chars, starting from the 2nd
    return typePrefix, messageContent
    
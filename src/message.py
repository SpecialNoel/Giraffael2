# message.py

# Functions here are used to argument messages transmitted
#   between clients and server.


# Return a copy of the message with trailing spaces or new line chars removed.
# Mainly used for removing the new line character at the end of the message.
def rstrip_message(message): # message is a string or a bytes
    return message.rstrip()


# Used to add a prefix to the message to indicate its usage.
# Note: this only applies to messages sent over the channel 
#   (i.e. already inside a room.)
# Type prefixes:
#   Normal: NOR
#   File:   FIL
# Format: type_prefix|message_content
def add_prefix_to_message(message, typePrefix): # message is a string or a bytes
    if isinstance(message, str):
        return (typePrefix+'|') + message
    elif isinstance(message, bytes):
        return (typePrefix+'|').encode() + message
    else:
        print('Message is neither a string nor a bytes-object.')
        return message


# Used to obtain the message without the prefix indicating its usage
def separate_type_prefix_from_message(message): # message is a string or a bytes
    if isinstance(message, str):
        typePrefix, messageContent = message.split('|', 1)
        return typePrefix, messageContent
    elif isinstance(message, bytes):
        typePrefix = message[:3] # first 3 chars
        messageContent = message[4:] # the rest chars, starting from the 5th
        return typePrefix, messageContent
    print('Message is neither a string nor a bytes-object.')
    return None, message
    
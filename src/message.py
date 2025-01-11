# message.py

# Functions here are used to argument messages transmitted
#   between clients and server.

# Return a copy of the message with trailing spaces or new line chars removed.
# Mainly used for removing the new line character at the end of the message.
def rstrip_message(message): # message is a string or a bytes
    return message.rstrip()

# message.py

# Functions here are used to argument messages transmitted
#   between clients and server.

# Return a copy of the string with trailing spaces or new line chars removed.
# Mainly used for removing the new line character at the end of the message.
# If message is empty, return the original message.
def rstrip_message(message): # message is a string
    if not message:
        return message
    return message.rstrip()

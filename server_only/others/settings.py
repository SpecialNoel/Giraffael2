# settings.py

# This file is used to store parameters of extra features (remote, OpenAI, TLS)
#   to be used in both client and server sides.

# File encryption and decryption with SHA256 already implemented in 
#   data transmission as a base feature of Giraffael 2 
# Note: not for normal messages yet. 

# EE2E is not implemented yet. 
# Purpose: encrypt data from sender to the intended recipient, ensuring only 
#          they can read it (not even the server should be able to decrypt it).

# If set to False: server will be hosted with the local machine's private IP.
# If set to True:  server will be hosted remotely on AWS ec2 instance, with
#                  the elastic IP assigned to that instance.
serverIsLocal = True

# If set to False: server will not be using OpenAI to generate message 
#                  suggestion.
# If set to True:  server will be using OpenAI for generating message 
#                  suggestion, upon client request.
usingOpenAI = True

# If set to False: both server and client will not be using TLS on the socket 
#                  to provide encryption of transmitted data.  
# If set to True:  both server and client will be using TLS on the socket to 
#                  provide encryption of transmitted data.
usingTLS = True

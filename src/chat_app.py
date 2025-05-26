# chat_app.py

# Assume in the "Giraffael2" folder:
# To run this script: python3 -m src.chat_app
# Then, run the client script: python3 -m src.client_only.client_core.client

from src.server_only.server_core.server import Server

class Chat_App:
    def __init__(self):
        server = Server()
        server.run_server()
     
if __name__=='__main__':  
    Chat_App()

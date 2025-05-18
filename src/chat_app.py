# chat_app.py

# Assume in the "src" folder:
# To run this script: python3 chat_app.py
# Then, run the client script: python3 client_only/client_core/client.py

from server_only.server_core.server import Server

class Chat_App:
    def __init__(self):
        server = Server()
        server.run_server()
     
if __name__=='__main__':  
    Chat_App()

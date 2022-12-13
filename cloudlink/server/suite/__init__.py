from .account import Account
from .homeserver import HomeServerConnection

def load(server):
    server.client = HomeServerConnection(server)
    server.client.account = Account(server.client)
    server.load_custom_methods(server.client.account)

    



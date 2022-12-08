from dataclass import dataclass
import sockets # for typing stuff
import bcript
import secrets
import uuid

@dataclass
class account:
    username: str
    password: bytes 
    _id: str

class Session:
    def __init__(self, CloudAccount, username, password):
       self.CA = CloudAccount
       self.db = self.CA.db

       usr = self.db.users.find_one({"username": username})
       if not usr: return

       if bcript.checkpw(password, usr['password']):
         self.authed = True
        else:
         self.authed = False
         return

        self.account = account(username, usr['password'], usr['_id'])
        self._token = secrets.token_urlsafe()
        
    
    @proprety
    def token(self): # self destructing proprety
        token = self._token

        if type(token) is str:
          self._token = bcript.hashpw(self._token, bcript.gensalt())
        

        return token



        
       


class CloudAccount:
    def __init__(self, home):
        self.home_server = home
        self.cloudlink = home.cl
        self.importer_ignore_functions = [self.isAuthed]
        self.db = home.db
 
    async def isAuthed(self, client) -> bool:
        return hasattr(client.session, "authed") and client.session.authed

    async def login(self, client, message, listener):
        if not 'username' in message:
            await self.cloudlink.send_code(client, "Syntax", extra_data={"key":"username"}, listener=listener)
            return
    
        if not 'password' in message:
            await self.cloudlink.send_code(client, "Syntax", extra_data={"key":"password"}, listener=listener)
            return 

        client.session = Session(self, message['username'], message['password'])
        if not client.session.authed:
            await self.cloudlink.send_code(client, "IDNotFound", listener=listener)
            return

        await self.cloudlink.send_packet_unicast(client, "direct", {"type":"auth", "username": message['username'], "token": client.session.token}, listener=listener)
        await self.cloudlink.send_code(client, "OK", listener=listener)

    async def signup(self, client, message, listener):
        #TODO: signup
        if not 'username' in message:
            self.cloudlink.send_code(client, "Syntax", extra_data={"key":"username"}, listener=listener)
            return
    
        usr = db.users.find_one({"username":message['username']})
        if usr:
            self.cloudlink.send_code(client, "IDConflict", listener=listener)
            return
        
        if not 'password' in message:
            self.cloudlink.send_code(client, "Syntax", extra_data={"key":"password"}, listener=listener)
            return 

        hashed = bcript.hashpw(message['password'], bcript.gensalt())
        self.db.users.insert_one({"password":hashed, "username":message['username'], "_id": uuid.uuid4().hex},)
        await self.cloudlink.send_code(client, "OK", listener=listener)

        self.cloudlink.set_client_username(client, message['username'])
        

   
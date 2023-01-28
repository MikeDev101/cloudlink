from dataclasses import dataclass
import socket # for typing stuff
import bcrypt
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
       if not usr: 
            self.authed = False
            return

       if bcrypt.checkpw(password.encode(), usr['password']):
         self.authed = True
       else:
         self.authed = False
         return

       self.account = account(username, usr['password'], usr['_id'])
       self._token = secrets.token_urlsafe()
       self.isserver = usr['server']
        
    
    @property
    def token(self): # self destructing proprety
        token = self._token

        if type(token) is str:
          self._token = bcrypt.hashpw(self._token.encode(), bcrypt.gensalt()) #type: ignore
        

        return token



        

class CloudAccount:
    def __init__(self, home):
        self.home_server = home
        self.cloudlink = home.cl
        self.cl = self.cloudlink # ???? past self
        self.importer_ignore_functions = [self.isAuthed]
        self.db = home.db
        self.logged_in_users = {}
        self.cloudlink.supporter.codes.update({
            "TokenNotFound":(self.cloudlink.supporter.error, 255, "TokenNotFound")
        })
 
    def isAuthed(self, client) -> bool:
        return hasattr(client, "session")  and hasattr(client.session, "authed") and client.session.authed

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

        self.logged_in_users[client.session.account._id] = client


        await self.cloudlink.send_code(client, "OK", listener=listener)
        client.server = client.session.isserver

    async def signup(self, client, message, listener):
       
        if not 'username' in message:
            await self.cloudlink.send_code(client, "Syntax", extra_data={"key":"username"}, listener=listener)
            return
    
        usr = self.db.users.find_one({"username":message['username']})
        if usr or message['username'].startswith("server"):
            await self.cloudlink.send_code(client, "IDConflict", listener=listener)
            return
        
        if not 'password' in message:
            await self.cloudlink.send_code(client, "Syntax", extra_data={"key":"password"}, listener=listener)
            return 

        hashed = bcrypt.hashpw(message['password'].encode(), bcrypt.gensalt())
        self.db.users.insert_one({"password":hashed, "username":message['username'], "_id": uuid.uuid4().hex, "server": False},)
        await self.cloudlink.send_code(client, "OK", listener=listener)

        self.cloudlink.set_client_username(client, message['username'])
        


    async def RegisterServerAccount(self, client, message, listener):
        if not self.isAuthed(client):
            await self.cl.send_code(client, "Refused", extra_data={"error":"noAuth"} ,listener=listener)
            return

        self.db.users.update_one({"_id": client.session.account._id}, { "$set": { "server": True }})

        await self.cl.send_code(client, "OK", listener=listener)
        client.server = True

    async def Server_LogClientIn(self, client, message, listener):
        # screw you, server login
        if not self.isAuthed(client):
            await self.cl.send_code(client, "Refused", extra_data={"error":"noAuth"} ,listener=listener)
            return
        
        if "userid" not in message:
            await self.cloudlink.send_code(client, "Syntax", extra_data={"key":"userid"}, listener=listener)
            return 

        if "user_token" not in message:
            await self.cloudlink.send_code(client, "Syntax", extra_data={"key":"user_token"}, listener=listener)
            return 

        # get data out for simplicity
        userid = message['userid']
        user_token = message['user_token']

        if userid not in self.logged_in_users: # UH WHAT THAT WAS if userid in self.logged_in_users
            await self.cloudlink.send_code(client, "IDNotFound", listener=listener)
            return
        
        _user = self.db.users.find_one({"username": userid})

        user = self.logged_in_users[_user["_id"]]

        if not bcrypt.checkpw(user_token.encode(), user.session.token):
            await self.cloudlink.send_code(client, "TokenNotFound", listener=listener)
            return

        await self.cloudlink.send_code(client, "OK", listener=listener, extra_data={"username": user.session.account.username})
        
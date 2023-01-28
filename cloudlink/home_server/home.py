import websockets
import asyncio
import json
from copy import copy

from pymongo import MongoClient
from .account import CloudAccount
from .disk import CloudDisk

try:
    from montydb import MontyClient
except ImportError:
    MontyClient = None

class DataBase:
    def __init__(self, type, uri):
      if type == MongoClient:
        self._db = MongoClient(uri)
      elif MontyClient is not None:
        self._db = MontyClient(uri)
      else:
        raise RuntimeError("<Home>: No DB Selected")
    
   


class Home:
    def __init__(self, server, db: DataBase):
        self.db = db._db.get_database("cl_homeserver")
        self.cl = server
        self.cl.supporter.disable_methods(["setid"])
        self.account = CloudAccount(self)
        self.disk = CloudDisk(self.account)

        self.cl.supporter.load_custom_methods(self.account)
        self.cl.supporter.load_custom_methods(self.disk)
        
    

    

    

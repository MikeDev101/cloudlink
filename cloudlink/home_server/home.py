import websockets
import asyncio
import json
from copy import copy

from pymongo import MongoClient
from .account import CloudAccount

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
    
    def __getattr__(self, name):
        return getattr(self._db, name)


class Home:
    def __init__(self, server:"Server", db: DataBase):
        self.db = DataBase
        self.cl = server
        self.cl.supporter.disable_methods("setid")
        self.account = CloudAccount(self)

        self.cl.supporter.load_custom_methods(self.account)
        
    

    

    
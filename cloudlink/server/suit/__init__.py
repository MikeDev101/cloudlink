import asyncio
from ._suit_cbs import suit_cbs


class SuitDB:
    def __init__(self, cl, type, path, db):
        self.cl = cl
        self.type = type
        self.db = None

        if type == "mongodb":
            from pymongo import MongoClient

            self.db = MongoClient(path)
        elif type == "tinydb":
            # drop in replacement for mongo, but is actualy tinyDB
            from tinymongo import TinyMongoClient

            self.db = TinyMongoClient(path)
        self.db = self.db[db]

    def find(self, collection, *args, **kwargs):

        return self.db[collection].find(*args, **kwargs)

    def find_one(self, collection, *args, **kwargs):
        return self.db[collection].find_one(*args, **kwargs)

    def insert_one(self, collection, data):
        return self.db[collection].insert_one(data)

    def update_one(self, collection, query, data):
        return self.db[collection].update_one(query, data)


class Suit:
    def __init__(self, cloudlink, suit_db):
        self.db = suit_db
        self.cl = cloudlink
        self.cl.suit = self
        self.cl.db = self.db
        self.callbacks = {}

    # suit imports
    def account(self):
        from .account import CloudAccount
        self.CA = CloudAccount(self.cl)
        self.cl.loadCustomCommands(self.CA)
        
        return self

    def disk(self):
        from .disk import CloudDisk
        self.CD = CloudDisk
        self.cl.loadCustomCommands(self.CD)
        return self

    def coin(self):
        from .coin import CloudCoin
        self.CC = CloudCoin(self.cl)
        self.cl.loadCustomCommands(self.CC)
        
        return self

    # allow multi cbs on the same cb
    def callback(self, callback, CB_ID=None):
        if CB_ID is None:
            CB_ID = callback.__name__

        if CB_ID in self.callbacks:
            self.callbacks[CB_ID].append(callback)
        else:
            self.callbacks[CB_ID] = [callback]
        return self

    async def call_callbacks(self, CB_ID, *args, **kwargs):
        if CB_ID not in self.callbacks:
            return
        lp = asyncio.get_event_loop()
        tasks = [lp.Task(c(*args, **kwargs)) for c in self.callbacks[CB_ID]]

        await asyncio.gather(*tasks)
        return self

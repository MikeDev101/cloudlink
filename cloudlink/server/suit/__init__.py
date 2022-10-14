import asyncio


class SuitDB:
    def __init__(self, cl, type, path, db):
        self.cl = cl
        self.type = type
        self.db = None
        if type == "mongodb":
            from pymongo import MongoClient

            db_obj = MongoClient(path)
        elif type == "Monty":
            # drop in replacement for mongo, but is actualy tinyDB
            from montydb import MontyClient
            db_obj = MontyClient(path)
        self.db = db_obj[db]
        if self.db  == db_obj:
          print("getting DB failed")
    def __getattr__(self, name):
      if self.db is None:
        raise AttributeError("Database not initialized")
      return getattr(self.db, name)

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
        self.cl.supporter.load_custom_methods(self.CA)
        return self

    def disk(self):
        from .disk import CloudDisk

        self.CD = CloudDisk(self.cl)
        self.cl.supporter.load_custom_methods(self.CD)
        return self

    def coin(self):
        from .coin import CloudCoin

        self.CC = CloudCoin(self.cl)
        self.cl.supporter.load_custom_methods(self.CC)
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

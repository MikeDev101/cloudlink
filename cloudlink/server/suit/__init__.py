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
    def _bind_cbs(self):
        self.cl.callback(self.cl.on_ulist, self._internal_cbs.on_ulist)
        self.cl.callback(self.cl.on_statuscode, self._internal_cbs.on_statuscode)
        self.cl.callback(self.cl.on_setid, self._internal_cbs.on_setid)
        self.cl.callback(self.cl.on_gmsg, self._internal_cbs.on_gmsg)
        self.cl.callback(self.cl.on_gvar, self._internal_cbs.on_gvar)
        self.cl.callback(self.cl.on_pvar, self._internal_cbs.on_pvar)
        self.cl.callback(self.cl.on_pmsg, self._internal_cbs.on_pmsg)
        self.cl.callback(self.cl.on_ping, self._internal_cbs.on_ping)

    def __init__(self, cloudlink, suit_db):
        self.db = suit_db
        self.cl = cloudlink
        self.cl.suit = self
        self.cl.db = self.db

        self._internal_cbs = suit_cbs(self.cl)
        self._bind_cbs()
        self.callbacks = {}

    # suit imports
    def account(self):
        from .account import CloudAccount

        self.cl.loadCustomCommands(CloudAccount)
        self.CA = self.cl.CloudAccount
        return self

    def disk(self):
        from .disk import CloudDisk

        self.cl.loadCustomCommands(CloudDisk)
        self.CD = self.cl.CloudDisk
        return self

    def coin(self):
        from .coin import CloudCoin

        self.cl.loadCustomCommands(CloudCoin)
        self.CC = self.cl.CloudCoin
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

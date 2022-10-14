from tinymongo import TinyMongoClient
import tinydb


class TinyMongoClient(TinyMongoClient):
    @property
    def _storage(self):
        return tinydb.storages.JSONStorage

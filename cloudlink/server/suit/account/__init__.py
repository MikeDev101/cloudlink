import asyncio
import bcrypt
import uuid
import datetime
import time
import secrets


class CloudAccount:
    def __init__(self, server):
        self.cl = server
        self.suit = self.cl.suit
        self.db = self.cl.db
        self.supporter = self.cl.supporter

        self.supporter.codes.update(
            {
                "AccountExists": ("E", 112, "Account already exists"),
                "AccountNotFound": ("E", 113, "Account not found"),
                "NotLoggedIn": ("I", 115, "Account Not logged in"),
            }
        )
        self.cl.disabled_methods.add("setid")
        self.importer_ignore_functions = ["IsAuthed"]

    # public API
    def IsAuthed(self, client):
        if not client.username_set:
            return False

        usr = self.db.users.find_one({"username": client.friendly_username})
        if not usr:
            return False

        # checking if user session is valid
        if type(usr["session"]["token"]) is None:
            return False

        if time.time() - usr["session"]["timeout"] > 2700:
            self.db.users.update_one(
                {"username": client.friendly_username},
                {
                    "$set": {
                        "session": {"timeout": 0, "token": None, "refresh_token": None}
                    }
                },
            )

            return False

        return True

    # commands
    async def create_account(self, client, message, listener_detected, listener_id):

        if "password" not in message:
            await self.cl.send_code(
                client,
                "Syntax",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        if "username" not in message:
            await self.cl.send_code(
                client,
                "Syntax",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        if self.db.users.find_one({"username": message["username"]}):
            await self.cl.send_code(
                client, "AccountExists", listener_detected, listener_id
            )
            return

        self.db.users.insert_one(
            {
                "_id": uuid.uuid4().hex,
                "username": message["username"],
                "password": bcrypt.hashpw(
                    message["password"].encode(), bcrypt.gensalt()
                ),
                "created": datetime.datetime.now(),
                "session": {"token": None, "timeout": 0, "refresh_token": None},
            },
        )
        await self.cl.send_code(
            client,
            "OK",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )

    async def refresh_auth(
        self,
        client,
        message,
        listener_detected,
        listener_id,
    ):

        if "refresh_token" not in message:
            await self.cl.send_code(
                client,
                "Syntax",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        if not self.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.db.users.update_one(
            {
                "username": client.friendly_username,
                "session": {"refresh_token": message["refresh_token"]},
            },
            {
                "$set": {
                    "session": {
                        "timeout": time.time(),
                        "token": secrets.token_urlsafe(),
                        "refresh_token": secrets.token_urlsafe(),
                    }
                }
            },
        )

        usr = self.db.users.find_one({"username": client.friendly_username})
        await self.cl.send_packet_multicast(
            self.cl.clients.get_all_with_username(client.friendly_username),
            cmd="auth",
            val={
                "username": client.friendly_username,
                "token": usr["session"]["token"],
                "refresh_token": usr["session"]["refresh_token"],
            },
            quirk=self.cl.supporter.quirk_update_msg,
        )

    async def login(self, client, message, listener_detected, listener_id):
        usr = self.db.users.find_one({"username": message["username"]})
        if not usr:
            await self.cl.send_code(
                client,
                "AccountNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        if not bcrypt.hashpw(message["password"].encode(), usr["password"]):
            await self.cl.send_code(
                client,
                "AccountNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.cl.clients.set_username(client, usr["username"])

        token = secrets.token_urlsafe()
        refresh_token = secrets.token_urlsafe()
        self.db.users.update_one(
            {
                "username": usr["username"],
            },
            {
                "$set": {
                    "session": {
                        "timeout": time.time(),
                        "token": token,
                        "refresh_token": refresh_token,
                    }
                }
            },
        )

        await self.cl.send_packet_multicast(
            self.cl.clients.get_all_with_username(message["username"]),
            cmd="auth",
            val={
                "username": message["username"],
                "token": token,
                "refresh_token": refresh_token,
            },
            quirk=self.cl.supporter.quirk_update_msg,
        )

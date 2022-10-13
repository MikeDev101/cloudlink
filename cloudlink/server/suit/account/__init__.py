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

        self.supporter.codes.extend(
            {
                "AccountExists": "E: 112 | Account already exists",
                "AccountNotFound": "E: 113 | Account not found",
                "NotLoggedIn": "E: 115 | I: Account Not logged in",
            }
        )
        self.cl.disableCommands("setid")
        self.importer_ignore_functions = ["IsAuthed"]

    # public API
    def IsAuthed(self, client):
        if not client.username_set:
            return False

        usr = self.db.find_one({"username": client.username})
        if not usr:
            return False

        # checking if user session is valid
        if type(usr["session"]["token"]) is None:
            return False

        if time.time() - usr["session"]["timeout"] > 2700:
            self.db.update_one(
                {"username": client.username},
                {
                    "$set": {
                        "session": {"timeout": 0, "token": None, "refresh_token": None}
                    }
                },
            )

            return False

        return True

    # commands
    async def sign_up(self, client, message, listener_detected, listener_id, room_id):

        if "password" not in message:
            await self.supporter.sendCode(
                client,
                "Syntax",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        if "username" not in message:
            await self.supporter.sendCode(
                client,
                "Syntax",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        if not self.db.find_one({"username": message["username"]}):
            await self.cl.sendCode(
                client, "AccountExists", listener_detected, listener_id
            )
            return

        self.db.insert(
            "users",
            {
                "_id": uuid.uuid4(),
                "username": message["username"],
                "password": bcrypt.hashpw(message["password"], bcrypt.gensalt()),
                "created": datetime.datetime.now(),
                "session": {"token": None, "timeout": 0, "refresh_token": None},
            },
        )
        await self.supporter.sendCode(
            client,
            "OK",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )

    async def refresh_auth(
        self, client, message, listener_detected, listener_id, room_id
    ):

        if "refresh_token" not in message:
            await self.supporter.sendCode(
                client,
                "Syntax",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        if not self.IsAuthed(client):
            await self.supporter.sendCode(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.db.update_one(
            "users",
            {
                "username": client.username,
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

        await self.supporter.SendPacket(
            client,
            {
                "type": "auth",
                "username": client.username,
                "token": usr.session.token,
                "refresh_token": usr.session.refresh_token,
            },
        )

    async def sign_in(self, client, message, listener_detected, listener_id, room_id):
        usr = self.db.find_one("users", {"username": username})
        if not usr:
            await self.supporter.sendCode(
                client,
                "AccountNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        if not bcrypt.hashpw(message["password"], usr.password):
            await self.supporter.sendCode(
                client,
                "AccountNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        await self.cl.setClientUsername(client, usr.username)

        token = secrets.token_urlsafe()
        refresh_token = secrets.token_urlsafe()
        self.db.update_one(
            "users",
            {
                "username": client.username,
                "session": {"refresh_token": message["refresh_token"]},
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

        await self.supporter.SendPacket(
            client,
            {
                "type": "auth",
                "username": message["username"],
                "token": token,
                "refresh_token": refresh_token,
            },
        )

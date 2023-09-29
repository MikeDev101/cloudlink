"""
rooms_manager - Provides tools to search, add, and remove rooms from the server.
"""


class exceptions:
    class RoomDoesNotExist(Exception):
        """This exception is raised when a client accesses a room that does not exist"""
        pass

    class RoomAlreadyExists(Exception):
        """This exception is raised when attempting to create a room that already exists"""
        pass

    class RoomNotEmpty(Exception):
        """This exception is raised when attempting to delete a room that is not empty"""
        pass

    class NoResultsFound(Exception):
        """This exception is raised when there are no results for a room search request."""
        pass

    class RoomUnsupportedProtocol(Exception):
        """This exception is raised when a room does not support a client's protocol."""
        pass


class rooms_manager:
    def __init__(self, parent):
        # Inherit parent
        self.parent = parent

        # Storage of rooms
        self.rooms = dict()

        # Init exceptions
        self.exceptions = exceptions()

        # Init logger
        self.logging = parent.logging
        self.logger = self.logging.getLogger(__name__)

    def get(self, room_id):
        try:
            return self.find_room(room_id)
        except self.exceptions.NoResultsFound:
            # Return default dict
            return {
                "clients": dict(),
                "global_vars": dict(),
                "private_vars": dict()
            }

    def create(self, room_id):
        # Rooms may only have string names
        if type(room_id) != str:
            raise TypeError("Room IDs only support strings!")

        # Prevent re-declaring a room
        if self.exists(room_id):
            raise self.exceptions.RoomAlreadyExists

        # Create the room
        self.rooms[room_id] = {
            "clients": dict(),
            "global_vars": dict(),
            "private_vars": dict()
        }

        # Log creation
        self.parent.logger.debug(f"Created room {room_id}")

    def delete(self, room_id):
        # Rooms may only have string names
        if type(room_id) != str:
            raise TypeError("Room IDs only support strings!")

        # Check if the room exists
        if not self.exists(room_id):
            raise self.exceptions.RoomDoesNotExist

        # Prevent deleting a room if it's not empty
        if len(self.rooms[room_id]["clients"]):
            raise self.exceptions.RoomNotEmpty

        # Delete the room
        self.rooms.pop(room_id)

        # Log deletion
        self.parent.logger.debug(f"Deleted room {room_id}")

    def exists(self, room_id) -> bool:
        # Rooms may only have string names
        if type(room_id) != str:
            raise TypeError("Room IDs only support strings!")

        return room_id in self.rooms

    def subscribe(self, obj, room_id):
        # Rooms may only have string names
        if type(room_id) != str:
            raise TypeError("Room IDs only support strings!")

        # Check if room exists
        if not self.exists(room_id):
            self.create(room_id)

        room = self.rooms[room_id]

        # Create room protocol categories
        if obj.protocol not in room["clients"]:
            room["clients"][obj.protocol] = {
                "all": set(),
                "uuids": dict(),
                "snowflakes": dict(),
                "usernames": dict()
            }

        room_objs = self.rooms[room_id]["clients"][obj.protocol]

        # Exit if client has subscribed to the room already
        if str(obj.id) in room_objs["uuids"]:
            return

        # Add to room
        room_objs["all"].add(obj)
        room_objs["uuids"][str(obj.id)] = obj
        room_objs["snowflakes"][obj.snowflake] = obj

        # Create room username reference
        if obj.username not in room_objs["usernames"]:
            room_objs["usernames"][obj.username] = set()

        # Add to usernames reference
        room_objs["usernames"][obj.username].add(obj)

        # Add room to client object
        obj.rooms.add(room_id)

        # Log room subscribe
        self.parent.logger.debug(f"Subscribed client {obj.snowflake} to room {room_id}")

    def unsubscribe(self, obj, room_id):
        # Rooms may only have string names
        if type(room_id) != str:
            raise TypeError("Room IDs only support strings!")

        # Check if room exists
        if not self.exists(room_id):
            raise self.exceptions.RoomDoesNotExist

        room = self.rooms[room_id]["clients"][obj.protocol]

        # Check if a client has subscribed to a room
        if str(obj.id) not in room["uuids"]:
            return

        # Remove from room
        room["all"].remove(obj)
        room["uuids"].pop(str(obj.id))
        room["snowflakes"].pop(obj.snowflake)
        if obj in room["usernames"][obj.username]:
            room["usernames"][obj.username].remove(obj)

        # Remove empty username reference set
        if not len(room["usernames"][obj.username]):
            room["usernames"].pop(obj.username)

        room = self.rooms[room_id]["clients"]

        # Clean up room protocol categories
        if not len(room[obj.protocol]["all"]):
            room.pop(obj.protocol)

        # Remove room from client object
        obj.rooms.remove(room_id)

        # Log room unsubscribe
        self.parent.logger.debug(f"Unsubscribed client {obj.snowflake} from room {room_id}")

        # Delete empty room
        if not len(room):
            self.parent.logger.debug(f"Deleting emptied room {room_id}...")
            self.delete(room_id)

    def find_room(self, query):
        # Rooms may only have string names
        if type(query) != str:
            raise TypeError("Searching for room objects requires a string for the query.")
        if query in (room for room in self.rooms):
            return self.rooms[query]
        else:
            raise self.exceptions.NoResultsFound

    def find_obj(self, query, room):
        # Prevent accessing clients with usernames not being set
        if not len(query):
            raise self.exceptions.NoResultsFound

        # Locate client objects in room
        if query in room["usernames"]:
            return room["usernames"][query] # returns set of client objects
        elif query in self.get_uuids(room):
            return room["uuids"][query] # returns client object
        elif query in self.get_snowflakes(room):
            return room["snowflakes"][query] # returns client object
        else:
            raise self.exceptions.NoResultsFound

    def generate_userlist(self, room_id, protocol) -> list:
        userlist = list()

        room = self.get(room_id)["clients"][protocol]["all"]

        for obj in room:
            if not obj.username_set:
                continue

            userlist.append({
                "id": obj.snowflake,
                "username": obj.username,
                "uuid": str(obj.id)
            })

        return userlist

    def get_snowflakes(self, room) -> set:
        return set(obj for obj in room["snowflakes"])

    def get_uuids(self, room) -> set:
        return set(obj for obj in room["uuids"])

    async def get_all_in_rooms(self, rooms, protocol) -> set:
        obj_set = set()

        # Validate types
        if type(rooms) not in [list, set, str]:
            raise TypeError(f"Gathering all user objects in rooms requires using a list, set, or string! Got {type(rooms)}.")

        # Convert to set
        if type(rooms) == str:
            rooms = {rooms}
        if type(rooms) == list:
            rooms = set(rooms)

        # Collect all user objects in rooms
        async for room in self.parent.async_iterable(rooms):
            if protocol not in self.get(room)["clients"]:
                continue
            obj_set.update(self.get(room)["clients"][protocol]["all"])

        return obj_set

    async def get_specific_in_room(self, room, protocol, queries) -> set:
        obj_set = set()

        # Validate types
        if type(room) != str:
            raise TypeError(f"Gathering specific clients in a room only supports strings for room IDs.")
        if type(queries) not in [list, set, str]:
            raise TypeError(f"Gathering all user objects in a room requires using a list, set, or string! Got {type(queries)}.")

        # Just return an empty set if the room doesn't exist
        if not self.exists(room):
            return set()

        room = self.get(room)["clients"][protocol]

        # Convert queries to set
        if type(queries) == str:
            queries = {queries}
        if type(queries) == list:
            queries = set(queries)

        async for query in self.parent.async_iterable(queries):
            try:
                obj = self.find_obj(query, room)
                if type(obj) == set:
                    obj_set.update(obj)
                else:
                    obj_set.add(obj)
            except self.exceptions.NoResultsFound:
                continue

        return obj_set

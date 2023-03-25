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

    class RoomAlreadyJoined(Exception):
        """This exception is raised when a client attempts to join a room, but it was already joined."""
        pass

    class RoomNotJoined(Exception):
        """This exception is raised when a client attempts to access a room not joined."""
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
            return self.find_obj(room_id)
        except self.exceptions.NoResultsFound:
            return dict()

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
            "usernames": dict(),
            "global_vars": dict(),
            "private_vars": dict()
        }

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

    def exists(self, room_id):
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

        # Check if client has not subscribed to a room
        if obj in self.rooms[room_id]["clients"]:
            raise self.exceptions.RoomAlreadyJoined

        # Create room protocol categories
        if obj.protocol not in self.rooms[room_id]["clients"]:
            self.rooms[room_id]["clients"][obj.protocol] = set()

        # Add to room
        self.rooms[room_id]["clients"][obj.protocol].add(obj)

        # Create room username reference
        if obj.username not in self.rooms[room_id]["usernames"]:
            self.rooms[room_id]["usernames"][obj.username] = set()

        # Add to usernames reference
        self.rooms[room_id]["usernames"][obj.username].add(obj)

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

        # Check if a client has subscribed to a room
        if obj not in self.rooms[room_id]["clients"][obj.protocol]:
            raise self.exceptions.RoomNotJoined(f"Client was not found in room {room_id}!")

        # Remove from room
        self.rooms[room_id]["clients"][obj.protocol].remove(obj)

        # Clean up room protocol categories
        if not len(self.rooms[room_id]["clients"][obj.protocol]):
            self.rooms[room_id]["clients"].pop(obj.protocol)

        # Remove from username reference
        if obj.username in self.rooms[room_id]["usernames"]:
            self.rooms[room_id]["usernames"][obj.username].remove(obj)

        # Remove empty username reference set
        if not len(self.rooms[room_id]["usernames"][obj.username]):
            self.rooms[room_id]["usernames"].pop(obj.username)

        # Remove room from client object
        obj.rooms.remove(room_id)

        # Log room unsubscribe
        self.parent.logger.debug(f"Unsubscribed client {obj.snowflake} from room {room_id}")

        # Delete empty room
        if not len(self.rooms[room_id]["clients"]):
            self.parent.logger.debug(f"Deleting emptied room {room_id}...")
            self.delete(room_id)

    def find_obj(self, query):
        # Rooms may only have string names
        if type(query) != str:
            raise TypeError("Searching for room objects requires a string for the query.")
        if query in (room for room in self.rooms):
            return self.rooms[query]
        else:
            raise self.exceptions.NoResultsFound

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

        # Delete reference to room
        self.room_names.pop(room_id)

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

        # Add to room
        self.rooms[room_id]["clients"][obj.snowflake] = obj

    def unsubscribe(self, obj, room_id):
        # Rooms may only have string names
        if type(room_id) != str:
            raise TypeError("Room IDs only support strings!")

        # Check if room exists
        if not self.exists(room_id):
            raise self.exceptions.RoomDoesNotExist

        # Check if a client has subscribed to a room
        if obj not in self.rooms[room_id]["clients"]:
            raise self.exceptions.RoomNotJoined

        # Remove from room
        del self.rooms[room_id]["clients"][obj.snowflake]

    def find_obj(self, query):
        # Rooms may only have string names
        if type(query) != str:
            raise TypeError("Searching for room objects requires a string for the query.")
        if query in (room for room in self.rooms):
            return self.rooms[query]
        else:
            raise self.exceptions.NoResultsFound

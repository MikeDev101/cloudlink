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

    class RoomsNotJoined(Exception):
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

    def create(self, room_id, supported_protocols=set):
        if type(room_id) not in [str, int, float, bool]:
            raise TypeError("Room IDs only support strings, booleans, or numbers!")

        if self.exists(room_id):
            raise self.exceptions.RoomAlreadyExists

        # Create the room
        self.rooms[room_id] = {
            "clients": set(),
            "supported_protocols": supported_protocols,
            "global_variables": set()
        }

    def delete(self, room_id):
        if not self.exists(room_id):
            raise self.exceptions.RoomDoesNotExist

        if len(self.rooms[room_id]["clients"]):
            raise self.exceptions.RoomNotEmpty

        # Delete the room
        self.rooms.pop(room_id)

    def exists(self, room_id):
        return room_id in self.rooms

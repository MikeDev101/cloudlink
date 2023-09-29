"""
clients_manager - Provides tools to search, add, and remove clients from the server.
"""


class exceptions:
    class ClientDoesNotExist(Exception):
        """This exception is raised when a client object does not exist"""
        pass

    class ClientAlreadyExists(Exception):
        """This exception is raised when attempting to add a client object that is already present"""
        pass

    class ClientUsernameAlreadySet(Exception):
        """This exception is raised when a client attempts to set their friendly username, but it was already set."""
        pass

    class ClientUsernameNotSet(Exception):
        """This exception is raised when a client object has not yet set it's friendly username."""
        pass

    class NoResultsFound(Exception):
        """This exception is raised when there are no results for a client search request."""
        pass

    class ProtocolAlreadySet(Exception):
        """This exception is raised when attempting to change a client's protocol."""
        pass


class clients_manager:
    def __init__(self, parent):
        # Inherit parent
        self.parent = parent

        # Create attributes for storage/searching
        self.clients = set()
        self.snowflakes = dict()
        self.protocols = dict()
        self.usernames = dict()
        self.uuids = dict()

        # Init exceptions
        self.exceptions = exceptions()

        # Init logger
        self.logging = parent.logging
        self.logger = self.logging.getLogger(__name__)

    def __len__(self):
        return len(self.clients)

    def get_snowflakes(self):
        return set(obj.snowflake for obj in self.clients)

    def get_uuids(self):
        return set(str(obj.id) for obj in self.clients)

    def exists(self, obj):
        return obj in self.clients

    def add(self, obj):
        if self.exists(obj):
            raise self.exceptions.ClientAlreadyExists

        # Add object to set
        self.clients.add(obj)

        # Add to snowflakes
        self.snowflakes[obj.snowflake] = obj

        # Add to UUIDs
        self.uuids[str(obj.id)] = obj

    def remove(self, obj):
        if not self.exists(obj):
            raise self.exceptions.ClientDoesNotExist

        # Remove from all clients set
        self.clients.remove(obj)

        # Remove from snowflakes
        self.snowflakes.pop(obj.snowflake)

        # Remove from UUIDs
        self.uuids.pop(str(obj.id))

        # Remove from protocol references
        if obj.protocol_set:

            # Remove reference to protocol object
            if obj in self.protocols[obj.protocol]:
                self.protocols[obj.protocol].remove(obj)

            # Clean up unused protocol references
            if not len(self.protocols[obj.protocol]):
                del self.protocols[obj.protocol]

        # Remove client from username references
        if obj.username_set:

            # Remove reference to username object
            if obj.username in self.usernames:
                self.usernames[obj.username].remove(obj)

            # Clean up unused usernames
            if not len(self.usernames[obj.username]):
                del self.usernames[obj.username]

    def set_username(self, obj, username):
        if not self.exists(obj):
            raise self.exceptions.ClientDoesNotExist

        if obj.username_set:
            raise self.exceptions.ClientUsernameAlreadySet

        # Create username reference
        if username not in self.usernames:
            self.usernames[username] = set()

        # Create reference to object from its username
        self.usernames[username].add(obj)

        # Finally set attributes
        obj.username_set = True
        obj.username = username

    def set_protocol(self, obj, schema):
        if not self.exists(obj):
            raise self.exceptions.ClientDoesNotExist

        if obj.protocol_set:
            raise self.exceptions.ProtocolAlreadySet

        # If the protocol was not specified beforehand, create it
        if schema not in self.protocols:
            self.protocols[schema] = set()

        # Add client to the protocols identifier
        self.protocols[schema].add(obj)

        # Set client protocol
        obj.protocol = schema
        obj.protocol_set = True

    def find_obj(self, query):
        if type(query) not in [str, dict]:
            raise TypeError("Clients can only be usernames (str), snowflakes (str), UUIDs (str), or Objects (dict).")

        if query in self.usernames:
            return self.usernames[query]
        elif query in self.get_uuids():
            return self.uuids[query]
        elif query in self.get_snowflakes():
            return self.snowflakes[query]
        else:
            raise self.exceptions.NoResultsFound

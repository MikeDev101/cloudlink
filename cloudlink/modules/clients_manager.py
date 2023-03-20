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

        self.logger.debug(f"Adding client object: {obj}")

        # Add object to set
        self.clients.add(obj)
        self.logger.debug(f"Current clients set state: {self.clients}")

        # Add to snowflakes
        self.snowflakes[obj.snowflake] = obj
        self.logger.debug(f"Current snowflakes state: {self.snowflakes}")

        # Add to UUIDs
        self.uuids[str(obj.id)] = obj
        self.logger.debug(f"Current UUIDs state: {self.uuids}")

    def remove(self, obj):
        if not self.exists(obj):
            raise self.exceptions.ClientDoesNotExist

        self.logger.debug(f"Removing client object: {obj}")

        # Remove from all clients set
        self.clients.remove(obj)
        self.logger.debug(f"Current clients set state: {self.clients}")

        # Remove from snowflakes
        self.snowflakes.pop(obj.snowflake)
        self.logger.debug(f"Current snowflakes state: {self.snowflakes}")

        # Remove from UUIDs
        self.uuids.pop(str(obj.id))
        self.logger.debug(f"Current UUIDs state: {self.uuids}")

        # Remove from protocol references
        if obj.protocol_set:

            # Remove reference to protocol object
            if obj in self.protocols[obj.protocol]:
                self.logger.debug(f"Removing client {obj.snowflake} from protocol reference: {obj.protocol}")
                self.protocols[obj.protocol].remove(obj)

            # Clean up unused protocol references
            if not len(self.protocols[obj.protocol]):
                self.logger.debug(f"Removing protocol {obj.protocol.__qualname__} from protocols")
                del self.protocols[obj.protocol]

        # Remove client from username references
        if obj.username_set:

            # Remove reference to username object
            if obj.friendly_username in self.usernames:
                self.logger.debug(f"Removing client {obj.snowflake} from username reference: {obj.friendly_username}")
                self.usernames[obj.friendly_username].remove(obj)

            # Clean up unused usernames
            if not len(self.usernames[obj.friendly_username]):
                self.logger.debug(f"Removing empty username reference: {obj.friendly_username}")
                del self.usernames[obj.friendly_username]

    def set_username(self, obj, username):
        if not self.exists(obj):
            raise self.exceptions.ClientDoesNotExist

        if obj.username_set:
            raise self.exceptions.ClientUsernameAlreadySet

        self.logger.debug(f"Setting client {obj.snowflake}'s friendly username to {username}")

        # Create username reference
        if username not in self.usernames:
            self.logger.debug(f"Creating new username reference: {username}")
            self.usernames[username] = set()

        # Create reference to object from it's username
        self.usernames[username].add(obj)

        # Finally set attributes
        obj.username_set = True
        obj.friendly_username = username

    def set_protocol(self, obj, schema):
        if not self.exists(obj):
            raise self.exceptions.ClientDoesNotExist

        if obj.protocol_set:
            raise self.exceptions.ProtocolAlreadySet

        # If the protocol was not specified beforehand, create it
        if schema not in self.protocols:
            self.logger.debug(f"Adding protocol {schema.__qualname__} to protocols")
            self.protocols[schema] = set()

        self.logger.debug(f"Setting client {obj.snowflake}'s protocol to {schema.__qualname__}")

        # Add client to the protocols identifier
        self.protocols[schema].add(obj)

        # Set client protocol
        obj.protocol = schema
        obj.protocol_set = True

    def find_obj(self, query):
        if query in self.usernames:
            return self.usernames[query]
        elif query in self.get_uuids():
            return self.uuids[query]
        elif query in self.get_snowflakes():
            return self.snowflakes[query]
        else:
            raise self.exceptions.NoResultsFound

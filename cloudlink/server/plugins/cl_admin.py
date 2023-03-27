# Disable CL commands
#server.disable_command(cmd=command, schema=clpv4.schema)

# Enable CL commands
#server.enable_command(cmd=command, schema=clpv4.schema)

# Set maximum number of users
#server.max_clients = -1 # -1 for unlimited

class cl_admin:
    def __init__(self, server, clpv4):
        server.logging.info("Initializing CL Admin Extension...")

        # Example config
        #TODO: make this secure
        self.admin_users = {
            "admin": {
                "password": "cloudlink",
                "permissions": {
                    "disable_commands": True,
                    "enable_commands": True,
                    "close_connections": True,
                    "change_user_limit": True,
                    "view_rooms": True,
                    "create_rooms": True,
                    "modify_rooms": True,
                    "delete_rooms": True,
                    "view_client_data": True,
                    "modify_client_data": True,
                    "delete_client_data": True,
                    "view_client_ip": True,
                    "add_admin_users": True,
                    "modify_admin_users": True,
                    "delete_admin_users": True
                },
                "enforce_ip_whitelist": True,
                "ip_whitelist": [
                    "127.0.0.1"
                ]
            }
        }

        # Extend the clpv4 protocol's schemas
        clpv4.schema.admin_auth = {
            "cmd": {
                "type": "string",
                "required": True
            },
            "val": {
                "type": "dict",
                "required": True,
                "schema": {
                    "username": {"type": "string", "required": True},
                    "password": {"type": "string", "required": True}
                }
            }
        }

        # Extend the clpv4 protocol's statuscodes
        clpv4.statuscodes.admin_auth_ok = (clpv4.statuscodes.info, 200, "Admin authentication successful")
        clpv4.statuscodes.invalid_admin_login = (clpv4.statuscodes.error, 201, "Invalid admin login")
        clpv4.statuscodes.admin_auth_failure = (clpv4.statuscodes.error, 202, "Admin authentication failure")
        clpv4.statuscodes.admin_session_exists = (clpv4.statuscodes.info, 203, "Admin session already exists")
        clpv4.statuscodes.ip_not_whitelisted = (clpv4.statuscodes.info, 204, "IP address not whitelisted for admin authentication")

        # Add new commands to the protocol
        @server.on_command(cmd="admin_auth", schema=clpv4.schema)
        async def admin_auth(client, message):
            # Validate message schema
            if not clpv4.valid(client, message, clpv4.schema.admin_auth):
                return

            # Check if the client is not already authenticated as an admin
            if hasattr(client, "admin_user"):
                clpv4.send_statuscode(
                    client,
                    clpv4.statuscodes.admin_session_exists,
                    details=f"You are currently authenticated as user {client.admin_user}. To logout, simply close the websocket connection."
                )
                return

            # Get inputs
            username = message["val"]["username"]
            password = message["val"]["password"]
            server.logging.info(f"Client {client.snowflake} attempting to admin authenticate as {username}...")

            # Verify username
            if username not in self.admin_users:
                clpv4.send_statuscode(
                    client,
                    clpv4.statuscodes.invalid_admin_login,
                    details=f"There is no registered admin user {username}. Please try again."
                )
                return

            # Check if IP whitelist is being enforced
            if self.admin_users[username]["enforce_ip_whitelist"] and (clpv4.get_client_ip(client) not in self.admin_users[username]["ip_whitelist"]):
                clpv4.send_statuscode(
                    client,
                    clpv4.statuscodes.ip_not_whitelisted,
                    details=f"The user {username} has enabled IP whitelist enforcement. This IP address, {clpv4.get_client_ip(client)} is not whitelisted."
                )
                return

            # Verify password
            if password != self.admin_users[username]["password"]:
                clpv4.send_statuscode(
                    client,
                    clpv4.statuscodes.admin_auth_failure,
                    details=f"Invalid password for admin user {username}. Please try again."
                )
                return

            # Admin is authenticated
            client.admin_user = username
            clpv4.send_statuscode(client, clpv4.statuscodes.admin_auth_ok)

        #TODO: Add admin command for disabling commands
        @server.on_command(cmd="admin_disable_command", schema=clpv4.schema)
        async def disable_command(client, message):
            pass

        # TODO: Add admin command for enabling commands
        @server.on_command(cmd="admin_enable_command", schema=clpv4.schema)
        async def enable_command(client, message):
            pass

        # TODO: Add admin command for kicking clients
        @server.on_command(cmd="admin_close_connection", schema=clpv4.schema)
        async def close_connection(client, message):
            pass

        # TODO: Add admin command for changing maximum number of users connecting
        @server.on_command(cmd="admin_change_user_limit", schema=clpv4.schema)
        async def change_user_limit(client, message):
            pass

        # TODO: Add admin command for getting room state
        @server.on_command(cmd="admin_get_room", schema=clpv4.schema)
        async def get_room(client, message):
            pass

        # TODO: Add admin command for creating rooms
        @server.on_command(cmd="admin_create_room", schema=clpv4.schema)
        async def create_room(client, message):
            pass

        # TODO: Add admin command for modifying room state
        @server.on_command(cmd="admin_edit_room", schema=clpv4.schema)
        async def edit_room(client, message):
            pass

        # TODO: Add admin command for deleting rooms
        @server.on_command(cmd="admin_delete_room", schema=clpv4.schema)
        async def delete_room(client, message):
            pass

        # TODO: Add admin command for reading attributes from a client object
        @server.on_command(cmd="admin_get_client_data", schema=clpv4.schema)
        async def get_client_data(client, message):
            pass

        # TODO: Add admin command for modifying attributes from a client object
        @server.on_command(cmd="admin_edit_client_data", schema=clpv4.schema)
        async def edit_client_data(client, message):
            pass

        # TODO: Add admin command for deleting attributes from a client object
        @server.on_command(cmd="admin_delete_client_data", schema=clpv4.schema)
        async def get_room(client, message):
            pass

        # TODO: Add admin command for retrieving ip address of a client object
        @server.on_command(cmd="admin_get_client_ip", schema=clpv4.schema)
        async def get_client_ip(client, message):
            pass

        # TODO: Add admin command for creating admin users
        @server.on_command(cmd="admin_add_admin_user", schema=clpv4.schema)
        async def add_admin_user(client, message):
            pass

        # TODO: Add admin command for modifying admin user permissions
        @server.on_command(cmd="admin_modify_admin_user", schema=clpv4.schema)
        async def modify_admin_user(client, message):
            pass

        # TODO: Add admin command for deleting admin users
        @server.on_command(cmd="admin_delete_admin_user", schema=clpv4.schema)
        async def delete_admin_user(client, message):
            pass

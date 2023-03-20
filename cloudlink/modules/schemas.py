"""
schemas - A replacement for the validate() function in older versions.
"""


class schemas:
    # Schema for interpreting the Cloudlink protocol v4.0 (CLPv4) command set
    class clpv4:
        # Required - Defines the keyword to use to define the command
        command_key = "cmd"

        # Required - Defines the default schema to test against
        default = {
            "cmd": {
                "type": "string",
                "required": True
            },
            "val": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "number",
                    "boolean",
                    "dict",
                    "list",
                    "set",
                ],
                "required": False,
            },
            "name": {
                "type": "string",
                "required": False
            },
            "id": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number"
                ],
                "required": False
            },
            "listener": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number"
                ],
                "required": False
            },
            "rooms": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number",
                    "list",
                    "set"
                ],
                "required": False
            }
        }

        gmsg = {
            "cmd": {
                "type": "string",
                "required": True
            },
            "val": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "number",
                    "boolean",
                    "dict",
                    "list",
                    "set",
                ],
                "required": True
            },
            "listener": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number"
                ],
                "required": False
            },
            "rooms": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number",
                    "list",
                    "set"
                ],
                "required": False
            }
        }

        gvar = {
            "cmd": {
                "type": "string",
                "required": True
            },
            "name": {
                "type": "string",
                "required": True
            },
            "val": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "number",
                    "boolean",
                    "dict",
                    "list",
                    "set",
                ],
                "required": True
            },
            "listener": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number"
                ],
                "required": False
            },
            "rooms": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number",
                    "list",
                    "set"
                ],
                "required": False
            }
        }

        pmsg = {
            "cmd": {
                "type": "string",
                "required": True
            },
            "id": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "number",
                    "boolean",
                    "dict",
                    "list",
                    "set",
                ],
                "required": True
            },
            "val": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "number",
                    "boolean",
                    "dict",
                    "list",
                    "set",
                ],
                "required": True
            },
            "listener": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number"
                ],
                "required": False
            },
            "rooms": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number",
                    "list",
                    "set"
                ],
                "required": False
            }
        }

        pvar = {
            "cmd": {
                "type": "string",
                "required": True
            },
            "name": {
                "type": "string",
                "required": True
            },
            "id": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "number",
                    "boolean",
                    "dict",
                    "list",
                    "set",
                ],
                "required": True
            },
            "val": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "number",
                    "boolean",
                    "dict",
                    "list",
                    "set",
                ],
                "required": True
            },
            "listener": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number"
                ],
                "required": False
            },
            "rooms": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "number",
                    "list",
                    "set"
                ],
                "required": False
            }
        }

    # Schema for interpreting the Cloud Variables protocol used in Scratch 3.0
    class scratch:
        # Required - Defines the keyword to use to define the command
        command_key = "method"

        # Required - Defines the default schema to test against
        default = {
            "method": {
                "type": "string",
                "required": True
            },
            "name": {
                "type": "string",
                "required": False
            },
            "value": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "dict",
                    "list",
                    "set"
                ],
                "required": False
            },
            "project_id": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean"
                ],
                "required": False,
            },
            "user": {
                "type": "string",
                "required": False,
                "minlength": 1,
                "maxlength": 20
            }
        }

        handshake = {
            "method": {
                "type": "string",
                "required": True
            },
            "project_id": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean"
                ],
                "required": True,
            },
            "user": {
                "type": "string",
                "required": True,
            }
        }

        method = {
            "method": {
                "type": "string",
                "required": True
            },
            "name": {
                "type": "string",
                "required": True
            },
            "value": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "dict",
                    "list",
                    "set"
                ],
                "required": False
            },
            "project_id": {
                "type": [
                    "string",
                    "integer",
                    "float",
                    "boolean"
                ],
                "required": True,
            },
            "user": {
                "type": "string",
                "required": False,
                "minlength": 1,
                "maxlength": 20
            }
        }

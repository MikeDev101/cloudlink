# Schema for interpreting the Cloudlink protocol v4.0 (CLPv4) command set
class cl4_protocol:

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
                "dict",
                "list",
                "set"
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

    linking = {
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
            "required": True,
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
        }
    }

    setid = {
        "cmd": {
            "type": "string",
            "required": True
        },
        "val": {
            "type": "string",
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
                "dict",
                "list",
                "set"
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

    direct = {
        "cmd": {
            "type": "string",
            "required": True
        },
        "id": {
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
                "dict",
                "list",
                "set"
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

# Schema for interpreting the Cloud Variables protocol used in Scratch 3.0
class scratch_protocol:

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
        "new_name": {
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
        "new_name": {
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
            "required": True,
        },
        "user": {
            "type": "string",
            "required": False,
            "minlength": 1,
            "maxlength": 20
        }
    }

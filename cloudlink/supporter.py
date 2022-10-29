import sys
import traceback
from datetime import datetime


class supporter:
    def __init__(self, parent):
        self.parent = parent

        # Define protocol types
        self.proto_unset = "proto_unset"
        self.proto_cloudlink = "proto_cloudlink"
        self.proto_scratch_cloud = "proto_scratch_cloud"

        # Multicasting message quirks
        self.quirk_embed_val = "quirk_embed_val"
        self.quirk_update_msg = "quirk_update_msg"

        # Case codes
        self.valid = 0
        self.invalid = 1
        self.missing_key = 2
        self.not_a_dict = 3
        self.unknown_method = 4
        self.unknown_protocol = 5
        self.username_set = 6
        self.username_not_set = 7
        self.disabled_method = 8
        self.too_large = 9

        # Scratch error codes
        self.connection_error = 4000
        self.username_error = 4002
        self.overloaded = 4003
        self.unavailable = 4004
        self.refused_security = 4005

        # Status codes
        self.info = "I"
        self.error = "E"
        self.codes = {
            "Test": (self.info, 0, "Test"),
            "OK": (self.info, 100, "OK"),
            "Syntax": (self.error, 101, "Syntax"),
            "DataType": (self.error, 102, "Datatype"),
            "IDNotFound": (self.error, 103, "ID not found"),
            "IDNotSpecific": (self.error, 104, "ID not specific enough"),
            "InternalServerError": (self.error, 105, "Internal server error"),
            "EmptyPacket": (self.error, 106, "Empty packet"),
            "IDSet": (self.error, 107, "ID already set"),
            "Refused": (self.error, 108, "Refused"),
            "Invalid": (self.error, 109, "Invalid command"),
            "Disabled": (self.error, 110, "Command disabled"),
            "IDRequired": (self.error, 111, "ID required"),
            "IDConflict": (self.error, 112, "ID conflict"),
            "TooLarge": (self.error, 113, "Too large")
        }

        # Method default keys and permitted datatypes
        self.keydefaults = {
            "val": [str, int, float, dict],
            "id": [str, int, dict, set, list],
            "listener": [str, dict, float, int],
            "rooms": [str, list],
            "name": str,
            "user": str,
            "project_id": str,
            "method": str,
            "cmd": str,
            "value": [str, int, float]
        }

    # New and improved version of the message sanity checker.
    def validate(self, keys: dict, payload: dict, optional=None, sizes: dict = None):
        # Check if input datatypes are valid
        if optional is None:
            optional = []
        if (type(keys) != dict) or (type(payload) != dict):
            return self.not_a_dict

        for key in keys.keys():
            # Check if a key is present
            if (key in payload) or (key in optional):
                # Bypass checks if a key is optional and not present
                if (key not in payload) and (key in optional):
                    continue

                # Check if there are multiple supported datatypes for a key
                if type(keys[key]) == list:
                    # Validate key datatype
                    if not type(payload[key]) in keys[key]:
                        return self.invalid

                    # Check if the size of the payload is too large 
                    if sizes:
                        if (key in sizes.keys()) and (len(str(payload[key])) > sizes[key]):
                            return self.too_large

                else:
                    # Validate key datatype
                    if type(payload[key]) != keys[key]:
                        return self.invalid

                    # Check if the size of the payload is too large 
                    if sizes:
                        if (key in sizes.keys()) and (len(str(payload[key])) > sizes[key]):
                            return self.too_large
            else:
                return self.missing_key

        # Hooray, the message is sane
        return self.valid

    def full_stack(self):
        exc = sys.exc_info()[0]
        if exc is not None:
            f = sys.exc_info()[-1].tb_frame.f_back
            stack = traceback.extract_stack(f)
        else:
            stack = traceback.extract_stack()[:-1]
        trc = 'Traceback (most recent call last):\n'
        stackstr = trc + ''.join(traceback.format_list(stack))
        if exc is not None:
            stackstr += '  ' + traceback.format_exc().lstrip(trc)
        return stackstr

    def is_json(self, json_str):
        is_valid_json = False
        try:
            if type(json_str) == dict:
                is_valid_json = True
            elif type(json_str) == str:
                json_str = self.json.loads(json_str)
                is_valid_json = True
        except:
            is_valid_json = False
        return is_valid_json

    def get_client_ip(self, client: dict):
        if "x-forwarded-for" in client.request_headers:
            return client.request_headers.get("x-forwarded-for")
        elif "cf-connecting-ip" in client.request_headers:
            return client.request_headers.get("cf-connecting-ip")
        else:
            if type(client.remote_address) == tuple:
                return str(client.remote_address[0])
            else:
                return client.remote_address

    def generate_statuscode(self, code: str):
        if code in self.codes:
            c_type, c_code, c_msg = self.codes[code]
            return f"{c_type}:{c_code} | {c_msg}", c_code
        else:
            raise ValueError

    # Determines if a method 
    def detect_listener(self, message):
        validation = self.validate(
            {
                "listener": self.keydefaults["listener"]
            },
            message
        )

        match validation:
            case self.invalid:
                return None
            case self.missing_key:
                return None

        return message["listener"]

    # Internal usage only, not for use in Public API
    def get_rooms(self, client, message):
        rooms = set()
        if "rooms" not in message:
            rooms.update(client.rooms)
        else:
            if type(message["rooms"]) == str:
                message["rooms"] = [message["rooms"]]
            rooms.update(set(message["rooms"]))

            # Filter rooms client doesn't have access to
            for room in self.copy(rooms):
                if room not in client.rooms:
                    rooms.remove(room)
        return rooms

    # Disables methods. Supports disabling built-in methods for monkey-patching or for custom reimplementation.
    def disable_methods(self, functions: list):
        if type(functions) != list:
            raise TypeError

        for function in functions:
            if type(function) != str:
                continue

            if function not in self.parent.disabled_methods:
                self.parent.disabled_methods.add(function)

            self.parent.safe_methods.discard(function)

    # Support for loading custom methods. Automatically selects safe methods.
    def load_custom_methods(self, _class):
        for function in dir(_class):
            # Ignore loading private methods
            if "__" in function:
                continue

            # Ignore loading commands marked as ignore
            if hasattr(_class, "importer_ignore_functions"):
                if function in _class.importer_ignore_functions:
                    continue

            setattr(self.parent.custom_methods, function, getattr(_class, function))
            self.parent.safe_methods.add(function)

    # This initializes methods that are guaranteed safe to use. This mitigates the possibility of clients accessing
    # private or sensitive methods.
    def init_builtin_cl_methods(self):
        for function in dir(self.parent.cl_methods):
            # Ignore loading private methods
            if "__" in function:
                continue

            # Ignore loading commands marked as ignore
            if hasattr(self.parent.cl_methods, "importer_ignore_functions"):
                if function in self.parent.cl_methods.importer_ignore_functions:
                    continue

            self.parent.safe_methods.add(function)

    def log(self, event, force: bool = False):
        if self.parent.enable_logs or force:
            print(f"{self.timestamp()}: {event}")

    def timestamp(self):
        today = datetime.now()
        return today.strftime("%m/%d/%Y %H:%M.%S")

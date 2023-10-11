#!/usr/bin/env python3

# CloudLink 3.0 - Client Mode Example Code

from cloudlink import CloudLink
import time

def on_new_packet(message): # message value is automatically converted into a dictionary datatype
    print(message)

def on_connect(): # use to start other scripts, in this example we declare a username: "test"
    cl.sendPacket({"cmd": "setid", "val": "test"})

def on_error(error): # does this do something?
    print(error)

if __name__ == "__main__":
    cl = CloudLink() # Instanciate the module
    try:
        cl.client("ws://127.0.0.1:3000/",
        on_new_packet = on_new_packet,
        on_connect = on_connect,
        on_error = on_error) # Start the module in client mode, and define our callbacks
        
        while cl.mode == 2: # Some other spaghetti code to keep the script running while the connection is live
            time.sleep(0.1)
        
    except KeyboardInterrupt:
        cl.stop() # Stops the client and exits
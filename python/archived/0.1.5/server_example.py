#!/usr/bin/env python3

# CloudLink 3.0 - Server Mode Example Code

from cloudlink import CloudLink
import time

if __name__ == "__main__":
    cl = CloudLink() # Instanciate the module
    try:
        cl.host(port=3000) # Start the module in server mode, host on port 3000
        
        while cl.mode == 1: # Some other spaghetti code to keep the script running while the connection is live
            time.sleep(0.1)
        
    except KeyboardInterrupt:
        cl.stop() # Stops the server and exits
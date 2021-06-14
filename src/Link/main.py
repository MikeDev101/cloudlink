#!/usr/bin/env python3

from cloudlink import CloudLink

if __name__ == "__main__":
    cl = CloudLink() # Initialize CloudLink
    cl.host(3000) # Run websocket server on ws://localhost:3000/
from cloudlink import CloudLink

"""
CloudLink v0.1.7 Server Example

This code demonstrates how easy it is to connect run a server. It also shows how to write functions
to interact with CloudLink.

For more information, please visit https://hackmd.io/G9q1kPqvQT6NrPobjjxSgg

NOTICE ABOUT CALLBACKS
The on_packet callback differs in what it does when used in server
mode than it does in client mode.

In server mode, the on_packet callback will only return back packets
sent using the "direct" command, and will return the value of "val".

If a client sends {"cmd": "direct", "val": "test"}, the server will
take this message and callback the on_packet callback here, only
returning the value "test" as the message.

In client mode, the message will return the entire packet.

As shown above, if a client sends {"cmd": "test", "val": "test", "id": "(YOUR ID HERE)"}
to (YOUR ID HERE), the on_packet callback will return the entire
JSON as the message.
"""

def on_packet(message):
    print(message)
    cl.sendPacket({"cmd": "statuscode", "val": cl.codes["Test"], "id": message["id"]})
    cl.sendPacket({"cmd": "direct", "val": message["val"], "id": message["id"]})
    print(cl.getUsernames())

if __name__ == "__main__":
    cl = CloudLink(debug=True)
    # Instanciates a CloudLink object into memory.
    
    cl.callback("on_packet", on_packet)
    # Create callbacks to functions.
    
    cl.setMOTD("CloudLink test", enable=True)
    # Sets the server Message of the Day.
    
    cl.server()
    # Start CloudLink and run as a server.

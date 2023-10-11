from cloudlink import CloudLink

"""
CloudLink v0.1.7 Client Example

This code demonstrates how easy it is to connect to a server. It also shows how to write functions
to interact with CloudLink.

For more information, please visit https://hackmd.io/G9q1kPqvQT6NrPobjjxSgg
"""

def on_connect():
    print("I am now connected!")
    cl.sendPacket({"cmd": "setid", "val": str(input("Enter a username... "))})

def on_error(error):
    print("Oops, I got an error! {0}".format(error))

def on_packet(message):
    print("I got a new message! {0}".format(message))
    print(cl.getUsernames())
    
    """
    The on_packet callback differs in what it does when used in server
    mode than it does in client mode.
    
    In server mode, the on_packet callback will only return back packets
    sent using the "direct" command, and will return the value of "val".
    
    If a client sends {"cmd": "direct", "val": "test"}, the server will
    take this message and callback the on_packet callback here, only
    returning the value "test" as the message.
    
    In client mode, the message will return all JSON with only modifications
    to remove the ID (if we're sending packets to someone, they don't need extra
    garbage data telling that it's theirs), and adds the "origin" value to tell
    the client who the packet was sent from.
    
    As shown above, if a client sends {"cmd": "test", "val": "test", "id": "(YOUR ID HERE)"}
    to (YOUR ID HERE), the on_packet callback will return
    {"cmd" "test", "val": "test", "origin" "(CLIENT'S ID)"}
    """

def on_close():
    print("Goodbye!")

if __name__ == "__main__":
    cl = CloudLink(debug=True) 
    # Instanciates a CloudLink object into memory.
    
    cl.callback("on_packet", on_packet)
    cl.callback("on_error", on_error)
    cl.callback("on_connect", on_connect)
    cl.callback("on_close", on_close)
    # Create callbacks to functions.
    
    cl.client()
    # Start CloudLink and run as a client.
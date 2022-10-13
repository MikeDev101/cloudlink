from cloudlink import cloudlink

class callback_examples:
    def __init__(self):
        pass

    def on_connect(self, client):
        #print(f"Client {client.obj_id} connected")
        client.set_username(str(client.obj_id))
        client.send_gmsg("test")
    
    def on_close(self, client):
        #print(f"Client {client.obj_id} disconnected")
        pass
    
    def username_set(self, client):
        #print(f"Client {client.obj_id}'s username was set!")
        pass
    
    def on_gmsg(self, client, message, listener_detected, listener_id):
        #print(f"Client {client.obj_id} got gmsg {message['val']}")
        pass

if __name__ == "__main__":
    cl = cloudlink()
    example = callback_examples()
    multi_client = cl.multi_client(async_client = False, logs = True)
    for x in range(25):
        client = multi_client.spawn(x, "ws://127.0.0.1:3000/")
        # Binding events - This example binds functions to certain events
        client.bind_event(client.events.on_connect, example.on_connect) # When a client connects, all functions bound to this event will fire.
        client.bind_event(client.events.on_close, example.on_close) # When a client disconnects, all functions bound to this event will fire.
        client.bind_event(client.events.on_username_set, example.username_set) # When a client disconnects, all functions bound to this event will fire.
        # Binding callbacks for commands - This example binds an event when a gmsg packet is handled.
        client.bind_callback_method(client.cl_methods.gmsg, example.on_gmsg)
    
    print("Waking up now")
    multi_client.run()
    input("All clients are ready. Press enter to shutdown.")
    multi_client.stop()
    input("All clients have shut down. Press enter to exit.")
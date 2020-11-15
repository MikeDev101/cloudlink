""" CloudCoin Server

This is the CloudCoin API service designed to communicate with a CloudLink API server.

For more details about the CloudLink API, please visit
https://github.com/MikeDev101/cloudlink

"""
servname = 'CC'
PORT = 3000

import websocket, json, threading, time, sys, traceback, os.path

if not os.path.isfile('cloudcoin.db'):
    spawn_db = open('cloudcoin.db', 'w+')
    spawn_db.write(json.dump({"users": [], "data": {}}))
    spawn_db.close()

if __name__ == "__main__":
    print("[ i ] Launching CloudCoin...")
    if "-ip" in sys.argv:
        ip = str(sys.argv[2])
        print("[ i ] Connecting to CloudLink API server using IP:", ip)
    else:
        print("[ i ] Using localhost to connect to CloudLink API server...")
        ip = "ws://127.0.0.1:3000/"

def user_IO_handler(cmd, user, data):
    print('[ i ] User "'+user+'": '+cmd+'...')
    time.sleep(0.05) # Delay to keep connection stable if using ultra-low latency connections
    if cmd == "PING":
        try:
            ws.send("<%cd>\n%"+servname+"%\n"+user+"\nOK")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
            ws.send("<%cd>\n%"+servname+"%\n"+user+"\n") # Return error to client
    elif cmd == "CHECK":
        try:
            # Reload cloudcoin file
            with open("cloudcoin.db") as json_file:
                userdata = json.load(json_file)
            if user in userdata['users']:
                raw_userdata = ((userdata['data'])[user]) #read data from disk
                rt_data = str(raw_userdata) #read specific data slot
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%cd>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%cd>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "SPEND":
        try:
            # Reload cloudcoin file
            with open("cloudcoin.db") as json_file:
                userdata = json.load(json_file)
            if user in userdata['users']:
                if (len(str(data)) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    raw_userdata = ((userdata['data'])[user]) #read data from disk
                    raw_userdata = str(float(raw_userdata)-float(data)) #replace data in slot
                    if float(raw_userdata) < 0.0:
                        rt_data = "E:BALANCE_TOO_LOW"
                    else:
                        (userdata['data'])[user] = raw_userdata #update contents on disk
                        with open("cloudcoin.db", "w") as outfile:
                            json.dump(userdata, outfile)
                        rt_data = "OK"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%cd>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%cd>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "EARN":
        try:
            # Reload cloudcoin file
            with open("cloudcoin.db") as json_file:
                userdata = json.load(json_file)
            if user in userdata['users']:
                if (len(str(data)) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    raw_userdata = ((userdata['data'])[user]) #read data from disk
                    raw_userdata = str(float(raw_userdata)+float(data)) #replace data in slot
                    (userdata['data'])[user] = raw_userdata #update contents on disk
                    with open("cloudcoin.db", "w") as outfile:
                        json.dump(userdata, outfile)
                    rt_data = "OK"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%cd>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%cd>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "REGISTER":
        try:
            # Reload cloudcoin file
            with open("cloudcoin.db") as json_file:
                userdata = json.load(json_file)
            if not user in userdata['users']:
                raw_userdata = (userdata['users'])
                raw_userdata.append(str(user))
                with open("cloudcoin.db", "w") as outfile:
                    json.dump(userdata, outfile)
                raw_userdata = (userdata['data'])
                raw_userdata[str(user)] = "0.00"
                with open("cloudcoin.db", "w") as outfile:
                    json.dump(userdata, outfile)
                print("[ i ] Registered user "+user+" successfully.")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" from the CloudAccount API, but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
    else:
        print("[ ! ] Error on user thread: attempted to handle a packet for user",str(user),"but an exception occured: The packet data is corrupt or invalid.")
        ws.send("<%cd>\n%"+servname+"%\n"+user+"\nE:INVALID_CMD")

def on_message(ws, message):
    pTmp = json.loads(message) # Convert the message from str. to a dict. object
    # Spawn user thread to handle the I/O from the websockets.
    if str(pTmp["type"]) == "ru": #Refresh userlist return, DO NOT REMOVE
        ws.send("<%sn>\n%"+servname+"%")
    elif (pTmp['id'] == ("%"+servname+"%")): # confirm that the packet is being transmitted to the correct server
        if __name__ == "__main__":
            uTmp = json.loads(pTmp['data']) #Read the json-encoded packet, and spawn a thread to handle it
            uCMD = uTmp['cmd']
            uID = uTmp['id']
            uData = uTmp['data']
            
            tr = threading.Thread(target=user_IO_handler, args=(uCMD, uID, uData))
            tr.start()

def on_error(ws, error):
    print("[ ! ] Oops! An error occured:", str(error))

def on_close(ws):
    print("[OK] CloudCoin is now disconnected.")

def on_open(ws):
    ws.send("<%sn>\n%"+servname+"%")
    print("[OK] CloudCoin is connected to CloudLink.")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(("ws://127.0.0.1:"+str(PORT)+"/"), on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.run_forever()
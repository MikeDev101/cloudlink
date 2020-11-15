""" CloudAccount Server

This is the CloudAccount API service designed to communicate with a CloudLink API server.

For more details about the CloudLink API, please visit
https://github.com/MikeDev101/cloudlink

"""
servname = 'CA'
PORT = 3000

import websocket, json, threading, time, sys, traceback, os.path
from hashlib import sha256

if not os.path.isfile('cloudaccount.db'):
    spawn_db = open('cloudaccount.db', 'w+')
    spawn_db.write(json.dump({"users": [], "data": {}}))
    spawn_db.close()

if __name__ == "__main__":
    print("[ i ] Launching CloudAccount...")
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
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\nOK")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\n") # Return error to client
    elif cmd == "CHECK":
        try:
            # Reload cloudaccount file
            with open("cloudaccount.db") as json_file:
                userdata = json.load(json_file)
            if user in userdata['users']:
                raw_userdata = ((userdata['data'])[user]) #read data from disk
                rt_data = str(raw_userdata['isAuth']) #return auth state
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "LOGIN":
        try:
            # Reload cloudaccount file
            with open("cloudaccount.db") as json_file:
                userdata = json.load(json_file)
            if user in userdata['users']:
                if (len(data) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    raw_userdata = (userdata['data'][user]) #read data from disk
                    if (sha256(str(data).encode('utf-8')).hexdigest() == raw_userdata['pswd']):
                        raw_userdata['isAuth'] = True #replace data in slot
                        userdata['data'][user] = raw_userdata #update contents on disk
                        with open("cloudaccount.db", "w") as outfile:
                            json.dump(userdata, outfile)
                        rt_data = "OK"
                    else:
                        rt_data = "E:INVALID_PASSWORD"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "LOGOUT":
        try:
            # Reload cloudaccount file
            with open("cloudaccount.db") as json_file:
                userdata = json.load(json_file)
            if user in userdata['users']:
                if (len(data) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    raw_userdata = (userdata['data'][user]) #read data from disk
                    if raw_userdata['isAuth']:
                        raw_userdata['isAuth'] = False #replace data in slot
                        userdata['data'][user] = raw_userdata #update contents on disk
                        with open("cloudaccount.db", "w") as outfile:
                            json.dump(userdata, outfile)
                        rt_data = "OK"
                    else:
                        rt_data = "I:ALREADY_LOGGED_OUT"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "REGISTER":
        try:
            # Reload cloudaccount file
            with open("cloudaccount.db") as json_file:
                userdata = json.load(json_file)
            if user in userdata['users']: 
                rt_data = "I:ALREADY_REGISTERED"
            else:
                raw_userdata = (userdata['users'])
                raw_userdata.append(str(user))
                with open("cloudaccount.db", "w") as outfile:
                    json.dump(userdata, outfile)
                raw_userdata = (userdata['data'])
                raw_userdata[str(user)] = {"isAuth":"true", "pswd":str(sha256(str(data).encode('utf-8')).hexdigest())}
                with open("cloudaccount.db", "w") as outfile:
                    json.dump(userdata, outfile)
                ws.send('<%ps>\n%'+servname+'\n%CD%\n{"cmd":"REGISTER","id":"'+user+'", "data":""}\n') # Send register command to the CloudDisk API
                ws.send('<%ps>\n%'+servname+'\n%CC%\n{"cmd":"REGISTER","id":"'+user+'", "data":""}\n') # Send register command to the CloudCoin API
                print("[ i ] Registered user "+user+" successfully.")
                rt_data = 'OK'
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%ca>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    else:
        print("[ ! ] Error on user thread: attempted to handle a packet for user",str(user),"but an exception occured: The packet data is corrupt or invalid.")
        ws.send("<%ca>\n%"+servname+"%\n"+user+"\nE:INVALID_CMD")

#ws.send("<%ca>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n")

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
    print("[OK] CloudAccount is now disconnected.")

def on_open(ws):
    ws.send("<%sn>\n%"+servname+"%")
    print("[OK] CloudAccount is connected to CloudLink.") 

if __name__ == "__main__":
    ws = websocket.WebSocketApp(("ws://127.0.0.1:"+str(PORT)+"/"), on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.run_forever()
""" CloudCoin Server

This is the CloudCoin API service designed to communicate with a CloudLink API server.

For more details about the CloudLink API, please visit
https://github.com/MikeDev101/cloudlink

"""
import websocket, json, threading, time, sys, traceback, os

SERVERID = 'CC' #Will be seen as %CC% on the Link
IP = "ws://127.0.0.1:3000/"

def init_files():
    try:
        os.mkdir("./USERDATA")
        print("[ i ] Created userdata directory.")
    except:
        pass
    finally:
        print("[ i ] Initialized files.")

def user_IO_handler(cmd, user, data):
    print('[ i ] User "'+user+'": '+cmd+'...')
    if cmd == "PING":
        try:
            ws.send("<%cd>\n%"+SERVERID+"%\n"+user+"\nOK")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception ocdured:",str(e))
            ws.send("<%cd>\n%"+SERVERID+"%\n"+user+"\n") # Return error to client
    elif cmd == "CHECK":
        try:
            # Check the existence of a user in the USERDATA directory
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                rt_data = str(userdata['balance']) #read balance from disk
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%cd>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception ocdured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%cd>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "SPEND":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                if (len(data) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    userdata['balance'] = float(float(userdata['balance'])-float(data))
                    if userdata['balance'] < 0.0:
                        rt_data = "E:BALANCE_TOO_LOW"
                    else:
                        with open(('./USERDATA/'+str(user)), "w") as outfile:
                            json.dump(userdata, outfile)
                        rt_data = "OK"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%cd>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception ocdured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%cd>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "EARN":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                if (len(data) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    userdata['balance'] = float(float(userdata['balance'])+float(data)) #replace data on disk
                    with open(('./USERDATA/'+str(user)), "w") as outfile:
                        json.dump(userdata, outfile)
                    rt_data = "OK"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%cd>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception ocdured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%cd>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "REGISTER":
        try:
            userlist = os.listdir("./USERDATA")
            if not user in userlist:
                userdata = {}
                userdata["balance"] = 0.0
                with open(('./USERDATA/'+str(user)), "w+") as outfile:
                    json.dump(userdata, outfile)
                print("[ i ] Registered user "+user+" successfully.")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" from the CloudAccount API, but an exception ocdured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
    elif cmd == "DELETE":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                os.remove(('./USERDATA/'+str(user)))
                print("[ i ] Deleted user "+user+" successfully.")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" from the CloudAccount API, but an exception ocdured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
    else:
        print("[ ! ] Error on user thread: attempted to handle a packet for user",str(user),"but an exception ocdured: The packet data is corrupt or invalid.")
        ws.send("<%cd>\n%"+SERVERID+"%\n"+user+"\nE:INVALID_CMD")

def on_message(ws, message):
    pTmp = json.loads(message) # Convert the message from str. to a dict. object
    # Spawn user thread to handle the I/O from the websockets.
    if str(pTmp["type"]) == "ru": #Refresh userlist return, DO NOT REMOVE
        ws.send("<%sn>\n%"+SERVERID+"%")
    elif (pTmp['id'] == ("%"+SERVERID+"%")): # confirm that the packet is being transmitted to the correct server
        if __name__ == "__main__":
            uTmp = json.loads(pTmp['data']) #Read the json-encoded packet, and spawn a thread to handle it
            uCMD = uTmp['cmd']
            uID = uTmp['id']
            uData = uTmp['data']
            
            tr = threading.Thread(target=user_IO_handler, args=(uCMD, uID, uData))
            tr.start()

def on_error(ws, error):
    print("[ ! ] Oops! An error ocdured:", str(error))

def on_close(ws):
    print("[OK] CloudCoin is now disconnected.")

def on_open(ws):
    ws.send("<%sn>\n%"+SERVERID+"%")
    print("[OK] CloudCoin is connected to CloudLink.")

if __name__ == "__main__":
    init_files()
    print("[ i ] Launching CloudCoin...")
    ws = websocket.WebSocketApp(IP, on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.run_forever()
    

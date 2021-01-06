""" CloudAccount Server

This is the CloudAccount API service designed to communicate with a CloudLink API server.

For more details about the CloudLink API, please visit
https://github.com/MikeDev101/cloudlink

"""
import websocket, json, threading, time, sys, traceback, os
from hashlib import sha256

SERVERID = 'CA' #Will be seen as %CA% on the Link
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
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\nOK")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\n") # Return error to client
    elif cmd == "CHECK":
        try:
            # Check the existence of a user in the USERDATA directory
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                rt_data = str(userdata['isAuth']) #read data from disk
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "LOGIN":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                if (len(data) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    if (sha256(str(data).encode('utf-8')).hexdigest() == userdata['pswd']):
                        userdata['isAuth'] = True #replace data
                        with open(('./USERDATA/'+str(user)), "w") as outfile:
                            json.dump(userdata, outfile)
                        rt_data = "OK"
                        ws.send("<%lg>\n"+user) # Send signal to CloudLink AutoLogout to add to list
                    else:
                        rt_data = "E:INVALID_PASSWORD"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "LOGOUT":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                if (len(data) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    if userdata['isAuth']:
                        userdata['isAuth'] = False #replace data on disk
                        with open(('./USERDATA/'+str(user)), "w") as outfile:
                            json.dump(userdata, outfile)
                        rt_data = "OK"
                        ws.send("<%lo>\n"+user) # Send signal to CloudLink AutoLogout to remove from list
                    else:
                        rt_data = "I:ALREADY_LOGGED_OUT"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "AUTOLOGOUT":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                if (len(data) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    if userdata['isAuth']:
                        userdata['isAuth'] = False #replace data on disk
                        with open(('./USERDATA/'+str(user)), "w") as outfile:
                            json.dump(userdata, outfile)
                        print("[ i ] AutoLogout has logged out user "+user+".")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
    elif cmd == "REGISTER":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                if userdata['isAuth']:
                        userdata['pswd'] = sha256(str(data).encode('utf-8')).hexdigest() #change password in slot
                        with open(('./USERDATA/'+str(user)), "w") as outfile:
                            json.dump(userdata, outfile)
                        rt_data = "OK"
                        print("[ i ] Changed "+str(user)+"'s password.")
                else:
                    rt_data = "E:NOT_LOGGED_IN"
            else:
                userdata = {}
                userdata["isAuth"] = True
                userdata["pswd"] = str(sha256(str(data).encode('utf-8')).hexdigest())
                with open(('./USERDATA/'+str(user)), "w+") as outfile:
                    json.dump(userdata, outfile)
                ws.send('<%ps>\n%'+SERVERID+'\n%CD%\n{"cmd":"REGISTER","id":"'+user+'", "data":""}\n') # Send register command to the CloudDisk API
                ws.send('<%ps>\n%'+SERVERID+'\n%CC%\n{"cmd":"REGISTER","id":"'+user+'", "data":""}\n') # Send register command to the CloudCoin API
                print("[ i ] Registered user "+user+" successfully.")
                rt_data = 'OK'
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "DELETE":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                if userdata['isAuth']:
                    if (sha256(str(data).encode('utf-8')).hexdigest() == userdata['pswd']):
                        os.remove(('./USERDATA/'+str(user)))
                        ws.send('<%ps>\n%'+SERVERID+'\n%CD%\n{"cmd":"DELETE","id":"'+user+'", "data":""}\n') # Send delete command to the CloudDisk API
                        ws.send('<%ps>\n%'+SERVERID+'\n%CC%\n{"cmd":"DELETE","id":"'+user+'", "data":""}\n') # Send delete command to the CloudCoin API
                        rt_data = "OK"
                        print("[ i ] Deleted user "+user+" successfully.")
                    else:
                        rt_data = "E:INVALID_PASSWORD"
            else:
                rt_data = "E:ACC_ALREADY_DELETED_OR_NOT_FOUND"
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    else:
        print("[ ! ] Error on user thread: attempted to handle a packet for user",str(user),"but an exception occured: The packet data is corrupt or invalid.")
        ws.send("<%ca>\n%"+SERVERID+"%\n"+user+"\nE:INVALID_CMD")

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
    print("[ ! ] Oops! An error occured:", str(error))

def on_close(ws):
    print("[OK] CloudAccount is now disconnected.")

def on_open(ws):
    ws.send("<%sn>\n%"+SERVERID+"%")
    print("[OK] CloudAccount is connected to CloudLink.") 

if __name__ == "__main__":
    init_files()
    print("[ i ] Launching CloudAccount...")
    ws = websocket.WebSocketApp(IP, on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.run_forever()

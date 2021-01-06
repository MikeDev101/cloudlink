""" CloudDisk Server

This is the CloudDisk API service designed to communicate with a CloudLink API server.

For more details about the CloudLink API, please visit
https://github.com/MikeDev101/cloudlink

"""
import websocket, json, threading, time, sys, traceback, os

SERVERID = 'CD' #Will be seen as %CD% on the Link
IP = "ws://127.0.0.1:3000/"
FTP_DELAY = 0.5
MAX_CHUNK_SIZE = 1024

ftpUsers = []

def init_files():
    try:
        os.mkdir("./USERDATA")
        print("[ i ] Created userdata directory.")
    except:
        pass
    try:
        os.mkdir("./FTP")
        print("[ i ] Created FTP directory.")
    except:
        pass
    finally:
        print("[ i ] Initialized files.")

def user_IO_handler(cmd, user, data):
    print('[ i ] User "'+user+'": '+cmd+'...')
    if cmd == "PING":
        try:
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nOK")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\n") # Return error to client
    elif cmd == "READ":
        try:
            # Check the existence of a user in the USERDATA directory
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                rt_data = str(userdata[str(data)]) #read slot from disk
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "WRITE":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                userdata = json.loads(str(open(('./USERDATA/'+str(user)), "r").read()))
                if (len(data['data']) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    userdata[str(data['slot'])] = str(data['data']) #replace data on disk
                    with open(('./USERDATA/'+str(user)), "w") as outfile:
                        json.dump(userdata, outfile)
                    rt_data = "OK"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "REGISTER":
        try:
            userlist = os.listdir("./USERDATA")
            if not user in userlist:
                userdata = {}
                for x in range(10):
                    userdata[str(x+1)] = ""
                with open(('./USERDATA/'+str(user)), "w+") as outfile:
                    json.dump(userdata, outfile)
                print("[ i ] Registered user "+user+" successfully.")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" from the CloudAccount API, but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
    elif cmd == "DELETE":
        try:
            userlist = os.listdir("./USERDATA")
            if user in userlist:
                os.remove(('./USERDATA/'+str(user)))
                print("[ i ] Deleted user "+user+" successfully.")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" from the CloudAccount API, but an exception ocdured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
    else:
        print("[ ! ] Error on user thread: attempted to handle a packet for user",str(user),"but an exception occured: The packet data is corrupt or invalid.")

def ftp_IO_handler(cmd, user, data):
    print('[ i ] User "'+user+'": '+cmd+'...')
    if cmd == "GETLIST":
        try:
            ftpFileList = os.listdir("./FTP")
            rt_data = ''
            for x in range(len(ftpFileList)):
                rt_data = str(str(rt_data) + str(ftpFileList[x]) + ";")
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\n"+rt_data)
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e)+"/n"+str(traceback.format_exc()))
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\n") # Return error to client
    elif cmd == "GETINFO":
        try:
            # Reload ftp file
            ftpFileList = os.listdir("./FTP")
            if str(data) in ftpFileList:
                f = open(('./FTP/'+str(data)),"r")
                rt_data = str(len(f.read()))
            else:
                rt_data = 'E:FILE_NOT_FOUND'
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\n"+rt_data)
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\n") # Return error to client
    elif cmd == "GET":
        if not user in ftpUsers:
            ftpUsers.append(str(user))
            # Reload ftp file
            ftpFileList = os.listdir("./FTP")
            if str(data) in ftpFileList:
                ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nI:GETTING_READY")
                try:
                    dd = open(('./FTP/'+str(data)),"r").read()
                    n = MAX_CHUNK_SIZE
                    chunks = [dd[i:i+n] for i in range(0, len(dd), n)]
                    ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nI:SENDING")
                    print("[ i ] Sending "+str(len(chunks))+" chunks to user "+str(user)+"...")
                    for x in range(len(chunks)):
                        if user in ftpUsers:
                            ws.send("<%ftp>\n%"+SERVERID+"%\n"+user+"\n"+str(chunks[x]))
                            time.sleep(FTP_DELAY)
                    if user in ftpUsers:
                        ws.send("<%ftp>\n%"+SERVERID+"%\n"+user+"\n<TX>")
                        ftpUsers.remove(str(user))
                        print("[ i ] Done running FTP for user "+str(user)+".")
                        ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nI:DONE")
                except Exception as e:
                    print("[ ! ] Error on user thread: attempted to handle a FTP download command for user",str(user),"but an exception occured: "+str(e)+"\n"+str(traceback.format_exc()))
                    ws.send("<%ftp>\n%"+SERVERID+"%\n"+user+"\n<TX>")
                    ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR")
                    ftpUsers.remove(str(user))
            else:
                ws.send("<%ftp>\n%"+SERVERID+"%\n"+user+"\n<TX>")
                ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nE:FILE_NOT_FOUND")
    elif cmd == "PUT":
        try:
            if not user in ftpUsers:
                ftpUsers.append(str(user))
                ftpFileList = os.listdir("./FTP")
                if not str(data['fname']) in ftpFileList:
                    print("[ i ] Receiving new file "+str(data['fname'])+"...")
                else:
                    print("[ i ] Writing new data to file "+str(data['fname'])+"...")
                if not (len(data['fdata']) > 10000):
                    f = open(("./FTP/"+str(data['fname'])), "w+")
                    ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nI:WRITING")
                    print("[ i ] File "+str(data['fname'])+" is "+str(len(data['fdata']))+" bytes in size.")
                    f.write(data['fdata'])
                    f.close()
                    ws.send("<%ftp>\n%"+SERVERID+"%\n"+user+"\n<TX>")
                    ftpUsers.remove(str(user))
                    ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nI:DONE")
                else:
                    print("[ i ] File size is too large. Aborting upload.")
                    ws.send("<%ftp>\n%"+SERVERID+"%\n"+user+"\n<TX>")
                    ftpUsers.remove(str(user))
                    ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nE:DATA_TOO_LARGE")
                
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle a FTP upload command for user",str(user),"but an exception occured: "+str(e)+"\n"+str(traceback.format_exc()))
            ws.send("<%ftp>\n%"+SERVERID+"%\n"+user+"\n<TX>")
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR")
    elif cmd == "ABORT":
        if not user in ftpUsers:
            ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nE:NOT_IN_QUEUE")
        else:
            try:
                ftpUsers.remove(str(user))
                ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nI:ABORTED_OK")
                print("[ i ] Aborted FTP for user "+str(user)+".")
            except Exception as e:
                print("[ ! ] Error on user thread: attempted to handle a FTP start command for user",str(user),"but an exception occured: "+str(e)+"\n"+str(traceback.format_exc()))
                ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nE:INTERNAL_SERVER_ERR")
    else:
        print("[ ! ] Error on user thread: attempted to handle a packet for user",str(user),"but an exception occured: The packet data is corrupt or invalid.")
        ws.send("<%dd>\n%"+SERVERID+"%\n"+user+"\nE:INVALID_CMD")

def on_message(ws, message):
    pTmp = json.loads(message) # Convert the message from str. to a dict. object
    # Spawn user thread to handle the I/O from the websockets.
    if str(pTmp["type"]) == "ru": #Refresh userlist return, DO NOT REMOVE
        ws.send("<%sn>\n%"+SERVERID+"%")
    elif (pTmp['id'] == ("%"+SERVERID+"%")): # confirm that the packet is being transmitted to the correct server
        if str(pTmp['type']) == 'ftp': 
            if __name__ == "__main__":
                uTmp = json.loads(pTmp['data']) #Read the json-encoded packet, and spawn a thread to handle it
                uCMD = uTmp['cmd']
                uID = uTmp['id']
                uData = uTmp['data']
                tr = threading.Thread(target=ftp_IO_handler, args=(uCMD, uID, uData))
                tr.start()
        else:
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
    print("[OK] CloudDisk is now disconnected.")

def on_open(ws):
    ws.send("<%sn>\n%"+SERVERID+"%")
    print("[OK] CloudDisk is connected to CloudLink.") 

if __name__ == "__main__":
    init_files()
    print("[ i ] Launching CloudDisk...")
    ws = websocket.WebSocketApp(IP, on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.run_forever()

""" CloudDisk Server

This is the CloudDisk API service designed to communicate with a CloudLink API server.

For more details about the CloudLink API, please visit
https://github.com/MikeDev101/cloudlink

"""

servname = 'CD'
import websocket, json, threading, time, sys, traceback, os.path

if not os.path.isfile('clouddisk.db'):
    spawn_db = open('clouddisk.db', 'w+')
    spawn_db.write(json.dump({"users": [], "data": {}}))
    spawn_db.close()

if not os.path.isfile('config.dat'):
    spawn_cfg = open('clouddisk.db', 'w+')
    spawn_cfg.write(json.dump({"port":3000, "max_chunk_size":1024, "ftp_delay":1}))
    spawn_cfg.close()

if not os.path.isfile('ftp.txt'):
    spawn_cfg = open('ftp.txt', 'w+')
    spawn_cfg.write(json.dump({"files":["sample.txt"]}))
    spawn_cfg.close()

if not os.path.isfile('sample.txt'):
    spawn_cfg = open('sample.txt', 'w+')
    spawn_cfg.write("Hello, world!")
    spawn_cfg.close()

ctmp = open("config.dat", "r").read()
config = json.loads(ctmp)

PORT = int(config['port'])
print("PORT: "+str(PORT))
print("Max Chunk Size: "+str(config['max_chunk_size']))
print("FTP Delay: "+str(config['ftp_delay']))
ftpUsers = []

if __name__ == "__main__":
    print("[ i ] Launching CloudDisk...")
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
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\nOK")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\n") # Return error to client
    elif cmd == "READ":
        try:
            # Reload clouddisk file
            with open("clouddisk.db") as json_file:
                userdata = json.load(json_file)
            if user in userdata['users']:
                raw_userdata = ((userdata['data'])[user]) #read data from disk
                rt_data = str(raw_userdata[data]) #read specific data slot
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "WRITE":
        try:
            # Reload clouddisk file
            with open("clouddisk.db") as json_file:
                userdata = json.load(json_file)
            if user in userdata['users']:
                if (len(data['data']) > 1000):
                    rt_data = "E:DATA_TOO_LARGE"
                else:
                    raw_userdata = ((userdata['data'])[user]) #read data from disk
                    raw_userdata[data['slot']] = str(data['data']) #replace data in slot
                    (userdata['data'])[user] = raw_userdata #update contents on disk
                    with open("clouddisk.db", "w") as outfile:
                        json.dump(userdata, outfile)
                    rt_data = "OK"
            else:
                rt_data = 'E:ACC_NOT_FOUND'
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\n"+rt_data+"\n") # Return value to client
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client
    elif cmd == "REGISTER":
        try:
            # Reload clouddisk file
            with open("clouddisk.db") as json_file:
                userdata = json.load(json_file)
            if not user in userdata['users']:
                raw_userdata = (userdata['users'])
                raw_userdata.append(str(user))
                with open("clouddisk.db", "w") as outfile:
                    json.dump(userdata, outfile)
                raw_userdata = (userdata['data'])
                raw_userdata[str(user)] = {"1": "", "2": "", "3": "", "4": "", "5": "", "6": "", "7": "", "8": "", "9": "", "10": ""}
                with open("clouddisk.db", "w") as outfile:
                    json.dump(userdata, outfile)
                print("[ i ] Registered user "+user+" successfully.")
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" from the CloudAccount API, but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
    else:
        print("[ ! ] Error on user thread: attempted to handle a packet for user",str(user),"but an exception occured: The packet data is corrupt or invalid.")

def ftp_IO_handler(cmd, user, data):
    print('[ i ] User "'+user+'": '+cmd+'...')
    time.sleep(0.05) # Delay to keep connection stable if using ultra-low latency connections
    if cmd == "GETLIST":
        try:
            # Reload ftp file
            with open("ftp.txt") as json_file:
                ftpData = json.load(json_file)
            ftpFileList = list(ftpData['files'])
            rt_data = ''
            for x in range(len(ftpFileList)):
                rt_data = str(str(rt_data) + str(ftpFileList[x]) + ";")
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\n"+rt_data)
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e)+"/n"+str(traceback.format_exc()))
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\n") # Return error to client
    elif cmd == "GETINFO":
        try:
            # Reload ftp file
            with open("ftp.txt") as json_file:
                ftpData = json.load(json_file)
            ftpFileList = list(ftpData['files'])
            if str(data) in ftpFileList:
                f = open(str(data),"r")
                rt_data = str(len(f.read()))
            else:
                rt_data = 'E:FILE_NOT_FOUND'
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\n"+rt_data)
        except Exception as e:
            print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\n") # Return error to client
    elif cmd == "GET":
        if not user in ftpUsers:
            ftpUsers.append(str(user))
            # Reload ftp file
            with open("ftp.txt") as json_file:
                ftpData = json.load(json_file)
            ftpFileList = list(ftpData['files'])
            if str(data) in ftpFileList:
                ws.send("<%dd>\n%"+servname+"%\n"+user+"\nI:GETTING_READY")
                try:
                    dd = open(str(data),"r").read()
                    n = int(config['max_chunk_size'])
                    chunks = [dd[i:i+n] for i in range(0, len(dd), n)]
                    ws.send("<%dd>\n%"+servname+"%\n"+user+"\nI:SENDING")
                    print("[ i ] Sending "+str(len(chunks))+" chunks to user "+str(user)+"...")
                    for x in range(len(chunks)):
                        if user in ftpUsers:
                            ws.send("<%ftp>\n%"+servname+"%\n"+user+"\n"+str(chunks[x]))
                            time.sleep(int(config['ftp_delay']))
                    if user in ftpUsers:
                        ws.send("<%ftp>\n%"+servname+"%\n"+user+"\n<TX>")
                        ftpUsers.remove(str(user))
                        print("[ i ] Done running FTP for user "+str(user)+".")
                        ws.send("<%dd>\n%"+servname+"%\n"+user+"\nI:DONE")
                except Exception as e:
                    print("[ ! ] Error on user thread: attempted to handle a FTP start command for user",str(user),"but an exception occured: "+str(e)+"\n"+str(traceback.format_exc()))
                    ws.send("<%dd>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR")
                    ftpUsers.remove(str(user))
            else:
                ws.send("<%ftp>\n%"+servname+"%\n"+user+"\n<TX>")
                ws.send("<%dd>\n%"+servname+"%\n"+user+"\nE:FILE_NOT_FOUND")
    elif cmd == "ABORT":
        if not user in ftpUsers:
            ws.send("<%dd>\n%"+servname+"%\n"+user+"\nE:NOT_IN_QUEUE")
        else:
            try:
                ftpUsers.remove(str(user))
                ws.send("<%dd>\n%"+servname+"%\n"+user+"\nI:ABORTED_OK")
                print("[ i ] Aborted FTP for user "+str(user)+".")
            except Exception as e:
                print("[ ! ] Error on user thread: attempted to handle a FTP start command for user",str(user),"but an exception occured: "+str(e)+"\n"+str(traceback.format_exc()))
                ws.send("<%dd>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR")
    else:
        print("[ ! ] Error on user thread: attempted to handle a packet for user",str(user),"but an exception occured: The packet data is corrupt or invalid.")
        ws.send("<%dd>\n%"+servname+"%\n"+user+"\nE:INVALID_CMD")

def on_message(ws, message):
    pTmp = json.loads(message) # Convert the message from str. to a dict. object
    # Spawn user thread to handle the I/O from the websockets.
    if str(pTmp["type"]) == "ru": #Refresh userlist return, DO NOT REMOVE
        ws.send("<%sn>\n%"+servname+"%")
    elif (pTmp['id'] == ("%"+servname+"%")): # confirm that the packet is being transmitted to the correct server
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
    ws.send("<%sn>\n%"+servname+"%")
    print("[OK] CloudDisk is connected to CloudLink.") 

if __name__ == "__main__":
    ws = websocket.WebSocketApp(("ws://127.0.0.1:"+str(PORT)+"/"), on_open = on_open, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.run_forever()
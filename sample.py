""" 

Sample CloudLink Server

This is a sample project designed to communicate with a CloudLink API server.

This serves as a framework from which you can design server software that handles backend communications and data processing.

This sample server software also depends upon the sample cloudlink client project.

For more details about the CloudLink API, please visit
https://github.com/MikeDev101/cloudlink

"""

import websocket
import json
import threading
import time
import sys

if "-ip" in sys.argv:
  ip = str(sys.argv[1])
  print("[ i ] Connecting to CloudLink API server using IP:", ip)
else:
  print('[ i ] No CloudLink API server IP defined! (hint: use "-ip wss://your.ip.here:port.") Using defaults...')
  ip = "wss://9f016d3d6e02.ngrok.io/"
  
datafile = "userdata.json"

def user_IO_handler(cmd, user, data):
  print('[ i ] User "'+user+'": '+cmd+'...')
  # Reload userdata file
  with open(datafile) as json_file:
    userdata = json.load(json_file)
  time.sleep(0.05) # Delay to keep connection stable if using ultra-low latency connections
  if cmd == "GET_USER_DATA":
    if data in userdata['users']:
      try:
        raw_userdata = (userdata['data'])[data]
        ws.send("<%ps>\n%MS%\n"+user+"\n"+str(raw_userdata))
      except Exception as e:
        print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
        ws.send("<%ps>\n%MS%\n"+user+"\n0110;2;100;")
    else:
      ws.send("<%ps>\n%MS%\n"+user+"\n111;3;101;")

  elif cmd == "LOGIN":
    if user in userdata['users']:
      try:
        raw_userdata = (userdata['data'])[user]
        raw_userdata = raw_userdata.split(";")
        if not len(raw_userdata) == 3:
          del raw_userdata[3]
        raw_userdata[1] = "1"
        tmp = ""
        for x in raw_userdata:
          tmp = tmp + x + ";"
        (userdata['data'])[user] = tmp
        with open(datafile, "w") as outfile:
          json.dump(userdata, outfile)
        ws.send("<%ps>\n%MS%\n"+user+"\n1")
      except Exception as e:
        print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
        ws.send("<%ps>\n%MS%\n"+user+"\n2")
    else:
      ws.send("<%ps>\n%MS%\n"+user+"\n0")

  elif cmd == "LOGOUT":
    if user in userdata['users']:
      try:
        raw_userdata = (userdata['data'])[user]
        raw_userdata = raw_userdata.split(";")
        if not len(raw_userdata) == 3:
          del raw_userdata[3]
        raw_userdata[1] = "0"
        tmp = ""
        for x in raw_userdata:
          tmp = tmp + x + ";"
        (userdata['data'])[user] = tmp
        with open(datafile, "w") as outfile:
          json.dump(userdata, outfile)
        ws.send("<%ps>\n%MS%\n"+user+"\n1")
      except Exception as e:
        print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
        ws.send("<%ps>\n%MS%\n"+user+"\n2")
    else:
      ws.send("<%ps>\n%MS%\n"+user+"\n0")

  elif cmd == "REGISTER":
    if not user in userdata['users']:
      try:
        userdata['users'].append(user)
        (userdata['data'])[user] = "0000;0;000;"
        with open(datafile, "w") as outfile:
          json.dump(userdata, outfile)
        ws.send("<%ps>\n%MS%\n"+user+"\n1")
      except Exception as e:
        print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
        ws.send("<%ps>\n%MS%\n"+user+"\n2")
    else:
      ws.send("<%ps>\n%MS%\n"+user+"\n0")

  elif cmd == "PING":
    try:
      ws.send("<%ps>\n%MS%\n"+user+"\n1")
    except Exception as e:
      print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e))
      ws.send("<%ps>\n%MS%\n"+user+"\n0")

def on_message(ws, message):
  pTmp = json.loads(message)
  # Spawn user thread to handle the I/O from the websockets.
  if str(pTmp["type"]) == "ru":
    ws.send("<%sn>\n%MS%")
  else:
    if __name__ == "__main__":
      uTmp = json.loads(pTmp['data'])
      uCMD = uTmp['cmd']
      uID = uTmp['id']
      uData = uTmp['data']
      tr = threading.Thread(target=user_IO_handler, args=(uCMD, uID, uData))
      tr.start()

def on_error(ws, error):
  print("[ ! ] Oops! An error occured:", str(error))
def on_close(ws):
  print("[OK] Disconnected.")

def closer():
  input()
  print("[ i ] Disconnecting...")
  ws.send("<%ds>\n%MS%")
  ws.close()
  sys.exit()

def on_open(ws):
  ws.send("<%sn>\n%MS%")
  print("[OK] Connected to CloudLink API.")
  exiter = threading.Thread(target=closer)
  exiter.start()

if __name__ == "__main__":
  try:
    ws = websocket.WebSocketApp(ip, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
  except:
    print("[ i ] Exiting server...")
    ws.send("<%ds>\n%MS%")
    ws.close()
    sys.exit()

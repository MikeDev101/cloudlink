""" Sample CloudLink Server

This is a sample project designed to communicate with a CloudLink API server.

This serves as a framework from which you can design server software that handles backend communications and data processing.

This sample server software also depends upon the sample cloudlink client project.

For more details about the CloudLink API, please visit
https://github.com/MikeDev101/cloudlink

"""

import websocket, json, threading, time, sys, traceback
servname = 'MS'

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
      # Place any code you need here
      # If there's an error, the exception will be handled in the code below...
      ws.send("<%ps>\n%"+servname+"%\n"+user+"\nOK") # Return value to client
    except Exception as e:
      print("[ ! ] Error on user thread: attempted to handle "+cmd+" for user",str(user),"but an exception occured:",str(e),", and the traceback data reads the following:\n"+str(traceback.format_exc()))
      ws.send("<%ps>\n%"+servname+"%\n"+user+"\nE:INTERNAL_SERVER_ERR") # Return error to client

def on_message(ws, message):
  pTmp = json.loads(message) # Convert the message from str. to a dict. object
  # Spawn user thread to handle the I/O from the websockets.
  if (pTmp['id'] == ("%"+servname+"%")): # confirm that the packet is being transmitted to the correct server
    if str(pTmp["type"]) == "ru": #Refresh userlist return, DO NOT REMOVE
      ws.send("<%sn>\n%"+servname+"%")
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
  print("[OK] Disconnected.")

def on_open(ws):
  ws.send("<%sn>\n%"+servname+"%")
  print("[OK] Connected to CloudLink API.")
  print("[ i ] To terminate this application, simply stop the main server.")

if __name__ == "__main__":
  try:
    ws = websocket.WebSocketApp(ip, on_message = on_message, on_error = on_error, on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
  except:
    print("[ i ] Exiting sample server...")
    ws.send("<%ds>\n%"+servname+"%")
    ws.close()
    sys.exit()

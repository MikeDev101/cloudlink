"""
MikeDEV's CloudLink Server
CloudLink is a websocket extension for Scratch 3.0, which allows MMOs, Web Browsers, BBSs, chats, and more, all using Scratch 3.0. It's cloud variables, but better. 
Origial concept created in 2018.
Rewritten in 2020.
For more details about CloudLink, please visit
https://github.com/MikeDev101/cloudlink
"""
import asyncio, json, websockets, sys, threading, ssl

vers = "S2.2"
PORT = 3000 #Define default port if the code runs on it's own
enable_verbose_events = False #Leave verbose events off by default
global USERNAMES

STREAMS = {"gs": "", "dd":""} #Define data streams, will improve upon this design later
USERS = set() #create unorganized, non-indexed set of users
USERNAMES = [] #create organized, indexable list of users
USERSDICT = {} #dictionary for figuring out what user is which
POINTERDICT = {} #reverse of USERSDICT
SPECIALHANDSHAKES = [] #list of websocket objects for checking which client has enabled special new features
LISTENERS = {"users":[], "listeningToHost":[], "hosts":[], "hostUserList":{}, "hostData":[]} # Dictionary containing lists of all associated users listening to other IDs
LOGGEDIN = [] # List containing all logge-in IDs to CloudAccount

class CloudLink(object):
    def __init__(self, loop):
        self.loop = loop

    async def notify_state_global(): # Send global data to every client
        if USERS:
            try:
                for user in USERS:
                    if user in SPECIALHANDSHAKES:
                        message = json.dumps({"type":"sf", "data":{"type":"gs", "data":str(STREAMS["gs"])}})
                    else:
                        message = json.dumps({"type":"gs", "data":str(STREAMS["gs"])})
                    await asyncio.wait([user.send(message)])
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_global, here's the error:\n"+str(e))
    
    async def notify_state_linked_global(e, varmode, var, data): # Send global data to linked clients
        if USERS:
            try:
                if e in LISTENERS['hosts']:
                    for user in LISTENERS['hostUserList'][e]:
                        if varmode:
                            message = json.dumps({"type":"sf", "data":{"type":"vm", "mode":"g", "var":var, "data":data}})
                        else:
                            message = json.dumps({"type":"sf", "data":{"type":"lm", "mode":"g", "data":str(LISTENERS['hostData'][LISTENERS['hosts'].index(e)])}, "id":user})
                        await asyncio.wait([POINTERDICT[user].send(message)])
                else:
                    print("[ ! ] Error: An exception occured. For notify_state_linked_global, the server attempted to send an update to a nonexistent link.\n")
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_linked_global, here's the error:\n"+str(e))
    
    async def notify_state_var_global(var, data): # Send global variables to linked clients
        if USERS:
            try:
                for user in USERS:
                    message = json.dumps({"type":"sf", "data":{"type":"vm", "mode":"g", "var":var, "data":data}})
                    await asyncio.wait([user.send(message)])
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_var_global, here's the error:\n"+str(e))
    
    async def notify_state_private(e): # Send private data to specific client
        if USERS:
            try:
                if e in POINTERDICT:
                    if e in SPECIALHANDSHAKES:
                        message = json.dumps({"type":"sf","data":{"type":"ps", "data":str(STREAMS[e])},"id":str(e)})
                    else:
                        message = json.dumps({"type":"ps","data":str(STREAMS[e]),"id":str(e)})
                    await asyncio.wait([POINTERDICT[e].send(message)])
                else:
                    print("[ ! ] Error: Attempted to notify_state_private to an invalid ID.")
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_private, here's the error:\n"+str(e))
    
    async def notify_state_linked_private(e, data): # Send private data to specific client
        if USERS:
            try:
                if e in POINTERDICT:
                    message = json.dumps({"type":"sf", "data":{"type":"lm", "mode":"p", "data":data}, "id":e})
                    await asyncio.wait([POINTERDICT[e].send(message)])
                else:
                    print("[ ! ] Error: Attempted to notify_state_linked_private to an invalid ID.")
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_linked_private, here's the error:\n"+str(e))
    
    async def notify_state_var_private(e, var, data): # Send private data to specific client
        if USERS:
            try:
                if e in POINTERDICT:
                    message = json.dumps({"type":"sf", "data":{"type":"vm", "mode":"p", "var":var, "data":data}, "id":e})
                    await asyncio.wait([POINTERDICT[e].send(message)])
                else:
                    print("[ ! ] Error: Attempted to notify_state_var_private to an invalid ID.")
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_var_private, here's the error:\n"+str(e))

    async def notify_state_disk(e): # Send disk data to specific client
        if USERS:
            message = json.dumps({"type":"dd","data":str(STREAMS[e]),"id":str(e)})
            try:
                if e in POINTERDICT:
                    await asyncio.wait([POINTERDICT[e].send(message)])
                else:
                    print("[ ! ] Error: Attempted to notify_state_disk to an invalid ID.")
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_disk, here's the error:\n"+str(e))
    
    async def notify_state_ftp(e): # Send ftp data to specific client
        if USERS:
            message = json.dumps({"type":"ftp","data":str(STREAMS[e]),"id":str(e)})
            try:
                if e in POINTERDICT:
                    await asyncio.wait([POINTERDICT[e].send(message)])
                else:
                    print("[ ! ] Error: Attempted to notify_state_ftp to an invalid ID.")
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_ftp, here's the error:\n"+str(e))

    async def notify_state_coin(e): # Send coin data to specific client
        if USERS:
            message = json.dumps({"type":"cd","data":str(STREAMS[e]),"id":str(e)})
            try:
                if e in POINTERDICT:
                    await asyncio.wait([POINTERDICT[e].send(message)])
                else:
                    print("[ ! ] Error: Attempted to notify_state_coin to an invalid ID.")
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_coin, here's the error:\n"+str(e))
    
    async def notify_state_account(e): # Send account data to specific client
        if USERS:
            message = json.dumps({"type":"ca","data":str(STREAMS[e]),"id":str(e)})
            try:
                if e in POINTERDICT:
                    await asyncio.wait([POINTERDICT[e].send(message)])
                else:
                    print("[ ! ] Error: Attempted to notify_state_account to an invalid ID.")
            except Exception as e:
                print("[ ! ] Error: An exception occured. For notify_state_account, here's the error:\n"+str(e))

    async def update_username_lists(): # Send username list to every client
        if USERS:
            y = ""
            for x in range(len(USERNAMES)):
                y = str(y + USERNAMES[x] + ";")
            message = json.dumps({"type":"ul","data":str(y)})
            try:
                for user in USERS:
                    await asyncio.wait([user.send(message)])
            except Exception as e:
                print("[ ! ] Error: An exception occured. For update_username_lists, here's the error:\n"+str(e))

    async def refresh_username_lists(): # Send refresh command to every client
        if USERS:
            try:
                for user in USERS:
                    await asyncio.wait([user.send(json.dumps({"type":"ru","data":""}))])
            except Exception as e:
                print("[ ! ] Error: An exception occured. For refresh_username_lists, here's the error:\n"+str(e))

    async def register(websocket): #Create client session
        USERS.add(websocket)

    async def unregister(websocket): #End client session
        USERS.remove(websocket)

    async def server(websocket, path):
        global USERNAMES
        await CloudLink.register(websocket)
        print("[ i ] Connection detected...")
        if not websocket in USERSDICT:
            USERSDICT[websocket] = ""
        
        # Send global data stream directly to new link
        await websocket.send(json.dumps({"type":"gs","data":str(STREAMS["gs"])}))
        
        # Send username list directly to new link
        y = ""
        for x in range(len(USERNAMES)):
            y = str(y + USERNAMES[x] + ";")
        await websocket.send(json.dumps({"type":"ul","data":str(y)}))
        try:
            async for message in websocket:
                data = message.split("\n")
                if enable_verbose_events:
                    print("[ i ] Got packet: "+str(data))
                if data[0] == "<%gs>": # Global stream update command
                    STREAMS["gs"] = str(data[2])
                    await CloudLink.notify_state_global()
                elif data[0] == "<%ps>": # Private stream update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_private(str(data[2]))
                elif data[0] == "<%dd>": # CloudDisk API update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_disk(str(data[2]))
                elif data[0] == "<%cd>": # CloudCoin API update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_coin(str(data[2]))
                elif data[0] == "<%ca>": # CloudAccount API update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_account(str(data[2]))
                elif data[0] == "<%ftp>": # CloudDisk API FTP update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_ftp(str(data[2]))
                elif data[0] == "<%rf>": # Refresh user list
                    print("[ i ] Refreshing user list...")
                    USERNAMES = []
                    await CloudLink.update_username_lists()
                    await CloudLink.refresh_username_lists()
                elif data[0] == "<%ds>": # Disconnect command
                    if data[1] in USERNAMES:
                        print("[ i ] Disconnecting user:", str(data[1]))
                        if "%CA%" in USERNAMES:
                            if data[1] in LOGGEDIN:
                                print("[ i ] AutoLogout is running...")
                                await POINTERDICT["%CA%"].send(json.dumps({"type":"ps","id":"%CA%", "data":json.dumps({"cmd":"AUTOLOGOUT", "id":data[1], "data":""})}))
                                LOGGEDIN.remove(data[1])
                        USERNAMES.remove(str(data[1]))
                        STREAMS.pop(str(data[1]))
                        await CloudLink.unregister(websocket)
                        await CloudLink.update_username_lists()
                        # Remove user from listener if the user was listening to a link
                        if data[1] in LISTENERS['users']:
                            print("[ i ] User "+str(data[1])+" unlinking from listeners...")
                            # Check if the user was listening to another ID
                            if (LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])] in LISTENERS['hostUserList']) and (data[1] in LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]]):
                                print("[ i ] Detected a preexisting listener for user "+str(data[1])+"...")
                                tempList = LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]]
                                tempList.remove(data[1])
                                if len(tempList) == 0:
                                    print("[ i ] The Linked ID "+str(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])])+" contains no other connections. Now deleting...")
                                    del LISTENERS['hostData'][LISTENERS['hosts'].index(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])])]
                                    del LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]]
                                    LISTENERS['hosts'].remove(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])])
                            # If there is no other circumstances, delete user from the link list
                            del LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]
                            del LISTENERS['users'][LISTENERS['users'].index(data[1])]
                        if websocket in USERSDICT:
                            del USERSDICT[websocket]
                            del POINTERDICT[data[1]]
                elif data[0] == "<%sn>": # Append username command
                    if not data[1] in USERNAMES:
                        print("[ i ] Connected:", data[1])
                        USERNAMES.append(str(data[1]))
                        STREAMS[str(data[1])] = ""
                        USERSDICT[websocket] = data[1]
                        POINTERDICT[data[1]] = websocket
                        await CloudLink.update_username_lists()
                        print("[ i ] Usernames: "+str(USERNAMES))
                        #print("[ i ] Users Dictionary: "+str(USERSDICT))
                        #print("[ i ] Pointers Dictionary: "+str(POINTERDICT))
                elif data[0] == "<%sh>": # Enable special features
                    if websocket in USERS:
                        if not websocket in SPECIALHANDSHAKES:
                            SPECIALHANDSHAKES.append(websocket)
                            await websocket.send(json.dumps({"type":"direct","data":{"type":"vers","data":vers}}))
                            print("[ i ] Registered special features.")
                elif data[0] == "<%rl>": # Register listener
                    if not data[2] in LISTENERS['hosts']: # Spawn new objects in LISTENERS dictionary if host is new
                        LISTENERS['hosts'].append(data[2])
                        LISTENERS['hostData'].append("")
                        LISTENERS['hostUserList'][data[2]] = []
                    if not data[1] in LISTENERS['users']: # Spawn new objects in LISTENERS if user is not new
                        LISTENERS['users'].append(data[1])
                        LISTENERS['listeningToHost'].append(None)
                    # Verify that the host is not the same as the the user's current listening state
                    if not LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])] == data[2]:
                        print("[ i ] User "+str(data[1])+" linking to listener...")
                        # Check if the user was listening to another ID
                        if (LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])] in LISTENERS['hostUserList']) and (data[1] in LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]]):
                            print("[ i ] Detected a preexisting listener for user "+str(data[1])+"...")
                            tempList = LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]]
                            tempList.remove(data[1])
                            if len(tempList) == 0:
                                print("[ i ] The Linked ID "+str(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])])+" contains no other connections. Now deleting...")
                                del LISTENERS['hostData'][LISTENERS['hosts'].index(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])])]
                                del LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]]
                                LISTENERS['hosts'].remove(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])])
                        # If there is no other circumstances, overwrite currently listening ID
                        LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])] = data[2]
                        if not data[1] in LISTENERS['hostUserList'][data[2]]:
                            LISTENERS['hostUserList'][data[2]].append(data[1])
                        await CloudLink.notify_state_linked_global(data[2], False, None, None)
                    else:
                        print("[ i ] User is already linked to preexisting ID, ignoring...")
                elif data[0] == "<%rt>": # Unregister listener
                    if data[1] in LISTENERS['users']:
                        print("[ i ] User "+str(data[1])+" unlinking from listeners...")
                        # Check if the user was listening to another ID
                        if (LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])] in LISTENERS['hostUserList']) and (data[1] in LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]]):
                            print("[ i ] Detected a preexisting listener for user "+str(data[1])+"...")
                            tempList = LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]]
                            tempList.remove(data[1])
                            if len(tempList) == 0:
                                print("[ i ] The Linked ID "+str(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])])+" contains no other connections. Now deleting...")
                                del LISTENERS['hostData'][LISTENERS['hosts'].index(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])])]
                                del LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]]
                                LISTENERS['hosts'].remove(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])])
                        # If there is no other circumstances, delete user from the link list
                        del LISTENERS['listeningToHost'][LISTENERS['users'].index(data[1])]
                        del LISTENERS['users'][LISTENERS['users'].index(data[1])]
                    else:
                        print("[ i ] User "+str(data[1])+" already unlinked from listeners.")
                elif data[0] == "<%l_g>": # Global Link / Variable update
                    if data[1] == '0': # Linked Data update
                        LISTENERS['hostData'][LISTENERS['hosts'].index(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[2])])] = data[3]
                        await CloudLink.notify_state_linked_global(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[2])], False, None, None)
                    elif data[1] == '1': # Normal Variable update
                        await CloudLink.notify_state_var_global(data[3], data[4])
                    elif data[1] == '2': # Linked variable update
                        await CloudLink.notify_state_linked_global(LISTENERS['listeningToHost'][LISTENERS['users'].index(data[2])], True, data[3], data[4])
                elif data[0] == "<%l_p>": # Private Link / Variable update
                    if data[1] == '0': # Linked Data update
                        await CloudLink.notify_state_linked_private(data[3], data[4])
                    elif data[1] == "1": # Normal Variable update
                        await CloudLink.notify_state_var_private(data[3], data[4], data[5])
                    elif data[1] == "2": # Linked Variable update
                        if data[3] in LISTENERS['users'] and (LISTENERS['listeningToHost'][LISTENERS['users'].index(data[2])] == LISTENERS['listeningToHost'][LISTENERS['users'].index(data[3])]):
                            await CloudLink.notify_state_var_private(data[3], data[4], data[5])
                elif data[0] == "<%lo>": # AutoLogout | Logout
                    if data[1] in LOGGEDIN:
                        LOGGEDIN.remove(data[1])
                        print("[ i ] Removed user "+str(data[1])+" from AutoLogout.")
                elif data[0] == "<%lg>": # AutoLogout | Login
                    if not data[1] in LOGGEDIN:
                        LOGGEDIN.append(data[1])
                        print("[ i ] Added user "+str(data[1])+" to AutoLogout.")
                else: # Generic unknown command response
                    print("[ ! ] Error: Unknown command:", str(data))
        except Exception as e:
            print("[ ! ] Error: An exception occured. Here's the error:\n"+str(e))
        finally:
            if websocket in USERSDICT and str(USERSDICT[websocket]) in USERNAMES:
                print("[ i ] Disconnecting user: "+str(USERSDICT[websocket])+" abnormally...")
            else:
                print("[ i ] Disconnect detected...")
            
            # AutoLogout user if they forget / can't logout (due to a dropped connection)
            if websocket in USERSDICT and str(USERSDICT[websocket]) in USERNAMES:
                if str(USERSDICT[websocket]) in LOGGEDIN:
                    print("[ i ] AutoLogout is running...")
                    await POINTERDICT["%CA%"].send(json.dumps({"type":"ps","id":"%CA%", "data":json.dumps({"cmd":"AUTOLOGOUT", "id":USERSDICT[websocket], "data":""})}))
                    LOGGEDIN.remove(str(USERSDICT[websocket]))
            
            # Remove the websocket object if the associated user has registered for special features
            if websocket in SPECIALHANDSHAKES:
                SPECIALHANDSHAKES.remove(websocket)
                print("[ i ] Unregistered special features.")
            
            # Remove the websocket object if the associated user has registered a link listener
            if websocket in USERSDICT and str(USERSDICT[websocket]) in USERNAMES:
                if USERSDICT[websocket] in LISTENERS['users']:
                    print("[ i ] User "+str(USERSDICT[websocket])+" unlinking from listeners...")
                    # Check if the user was listening to another ID
                    if (LISTENERS['listeningToHost'][LISTENERS['users'].index(USERSDICT[websocket])] in LISTENERS['hostUserList']) and (USERSDICT[websocket] in LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(USERSDICT[websocket])]]):
                        print("[ i ] Detected a preexisting listener for user "+str(USERSDICT[websocket])+"...")
                        tempList = LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(USERSDICT[websocket])]]
                        tempList.remove(USERSDICT[websocket])
                        if len(tempList) == 0:
                            print("[ i ] The Linked ID "+str(LISTENERS['listeningToHost'][LISTENERS['users'].index(USERSDICT[websocket])])+" contains no other connections. Now deleting...")
                            del LISTENERS['hostData'][LISTENERS['hosts'].index(LISTENERS['listeningToHost'][LISTENERS['users'].index(USERSDICT[websocket])])]
                            del LISTENERS['hostUserList'][LISTENERS['listeningToHost'][LISTENERS['users'].index(USERSDICT[websocket])]]
                            LISTENERS['hosts'].remove(LISTENERS['listeningToHost'][LISTENERS['users'].index(USERSDICT[websocket])])
                    # If there is no other circumstances, delete user from the link list
                    del LISTENERS['listeningToHost'][LISTENERS['users'].index(USERSDICT[websocket])]
                    del LISTENERS['users'][LISTENERS['users'].index(USERSDICT[websocket])]
            
            # Delete the websocket object from the users dictionary to prevent unwanted indexing of a nonexistent pointer
            if websocket in USERSDICT:
                try:
                    if str(USERSDICT[websocket]) in USERNAMES:
                        USERNAMES.remove(str(USERSDICT[websocket]))
                except Exception as e:
                    print(str(e))
                del USERSDICT[websocket]
            
            # Remove the websocket from the userlist
            if websocket in USERS:
                await CloudLink.unregister(websocket) # Unregister the websocket object
            
            # Update all user's userlists
            await CloudLink.update_username_lists()
            print("[ i ] Usernames: "+str(USERNAMES))
            #print("[ i ] LISTENERS: "+str(LISTENERS))

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        cl = CloudLink(loop)
        start_server = websockets.serve(CloudLink.server, "localhost", PORT)
        print("MikeDEV's CloudLink Server - Version " + str(vers) + " | Now running on port " + str(PORT) + ".")
        cl.loop.run_until_complete(start_server)
        cl.loop.run_forever()
    except KeyboardInterrupt:
        print("[ i ] Stopping the CloudLink API server...")
        sys.exit()
    except Exception as e:
        print("[ ! ] Error! Stopping the CloudLink API server... "+str(e))
        sys.exit()

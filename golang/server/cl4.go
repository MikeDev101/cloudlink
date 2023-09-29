package cloudlink

import (
	"log"
)

type UserObject struct {
	Id       string      `json:"id,omitempty"`
	Username interface{} `json:"username,omitempty"`
	Uuid     string      `json:"uuid,omitempty"`
}

func CL4ProtocolDetect(client *Client) {
	if client.protocol == 0 {
		// Update client attributes
		client.Lock()
		client.protocol = 1 // CL4
		client.Unlock()

		// Creates default room - Should only be generated once per server restart
		defaultroom := client.manager.CreateRoom("default")

		// Add the client to the room
		defaultroom.SubscribeClient(client)
	}
}

func (room *Room) BroadcastUserlistEvent(event string, client *Client, exclude bool) {
	// Create a dummy manager for selecting clients
	dummy := DummyManager(room.name)

	// Separate compatible clients
	for _, roomclient := range room.clients {
		tmpclient := roomclient.TempCopy()

		// Exclude handler
		excludeclientid := client.TempCopy().id
		if exclude && (tmpclient.id == excludeclientid) {
			continue
		}

		// Require a set username and a compatible protocol
		if (tmpclient.username == nil) || (tmpclient.protocol != 1) {
			continue
		}

		// Add client if passed
		dummy.AddClient(tmpclient)
	}

	// Broadcast state
	MulticastMessage(dummy.clients, &PacketUPL{
		Cmd:   "ulist",
		Val:   client.GenerateUserObject(),
		Mode:  event,
		Rooms: room.name,
	})
}

func (room *Room) BroadcastGmsg(value interface{}) {
	// Update room gmsg state
	room.gmsgStateMutex.Lock()
	room.gmsgState = value
	room.gmsgStateMutex.Unlock()

	// Broadcast the new state
	room.gmsgStateMutex.RLock()
	MulticastMessage(room.clients, &PacketUPL{
		Cmd:   "gmsg",
		Val:   room.gmsgState,
		Rooms: room.name,
	})
	room.gmsgStateMutex.RUnlock()
}

func (room *Room) BroadcastGvar(name interface{}, value interface{}) {
	// Update room gmsg state
	room.gvarStateMutex.Lock()
	room.gvarState[name] = value
	room.gvarStateMutex.Unlock()

	// Broadcast the new state
	room.gvarStateMutex.RLock()
	MulticastMessage(room.clients, &PacketUPL{
		Cmd:   "gvar",
		Name:  name,
		Val:   room.gvarState[name],
		Rooms: room.name,
	})
	room.gvarStateMutex.RUnlock()
}

func (client *Client) RequireIDBeingSet(message *PacketUPL) bool {
	usernameunset := (client.TempCopy().username == nil)
	if usernameunset {
		UnicastMessage(client, &PacketUPL{
			Cmd:      "statuscode",
			Code:     "E:111 | ID required",
			CodeID:   111,
			Listener: message.Listener,
		})
	}
	return usernameunset
}

func (client *Client) HandleIDSet(message *PacketUPL) bool {
	usernameset := (client.TempCopy().username != nil)
	if usernameset {
		UnicastMessage(client, &PacketUPL{
			Cmd:      "statuscode",
			Code:     "E:107 | ID already set",
			CodeID:   107,
			Val:      client.GenerateUserObject(),
			Listener: message.Listener,
		})
	}
	return usernameset
}

// CL4MethodHandler is a method that s created when a CL-formatted message gets handled by MessageHandler.
func CL4MethodHandler(client *Client, message *PacketUPL) {
	// TODO: finish this
	switch message.Cmd {
	case "handshake":

		// Read attribute
		handshakeDone := (client.TempCopy().handshake)

		// Don't re-broadcast this data if the handshake command was already used
		if !handshakeDone {

			// Update attribute
			client.Lock()
			client.handshake = true
			client.Unlock()

			// Send the client's IP address
			if client.manager.Config.CheckIPAddresses {
				UnicastMessage(client, &PacketUPL{
					Cmd: "client_ip",
					Val: client.connection.Conn.RemoteAddr().String(),
				})
			}

			// Send the server version info
			UnicastMessage(client, &PacketUPL{
				Cmd: "server_version",
				Val: ServerVersion,
			})

			// Send MOTD
			if client.manager.Config.EnableMOTD {
				UnicastMessage(client, &PacketUPL{
					Cmd: "motd",
					Val: client.manager.Config.MOTDMessage,
				})
			}

			// Send Client's object
			UnicastMessage(client, &PacketUPL{
				Cmd: "client_obj",
				Val: client.GenerateUserObject(),
			})

			// Send gmsg, ulist, and gvar states
			rooms := client.TempCopy().rooms
			for _, room := range rooms {
				UnicastMessage(client, &PacketUPL{
					Cmd:   "gmsg",
					Val:   room.gmsgState,
					Rooms: room.name,
				})
				UnicastMessage(client, &PacketUPL{
					Cmd:   "ulist",
					Mode:  "set",
					Val:   room.GenerateUserList(),
					Rooms: room.name,
				})
				room.gvarStateMutex.RLock()
				for name, value := range room.gvarState {
					UnicastMessage(client, &PacketUPL{
						Cmd:   "gvar",
						Name:  name,
						Val:   value,
						Rooms: room.name,
					})
				}
				room.gvarStateMutex.RUnlock()
			}
		}

		// Send status code
		UnicastMessage(client, &PacketUPL{
			Cmd:    "statuscode",
			Code:   "I:100 | OK",
			CodeID: 100,
		})

	case "gmsg":
		// Check if required Val argument is provided
		switch message.Val.(type) {
		case nil:
			UnicastMessage(client, &PacketUPL{
				Cmd:     "statuscode",
				Code:    "E:101 | Syntax",
				CodeID:  101,
				Details: "Message missing required val key",
			})
			return
		}

		// Handle multiple types for room
		switch message.Rooms.(type) {

		// Value not specified in message
		case nil:
			// Use all subscribed rooms
			rooms := client.TempCopy().rooms
			for _, room := range rooms {
				room.BroadcastGmsg(message.Val)
			}

		// Multiple rooms
		case []any:
			for _, room := range message.Rooms.([]any) {
				rooms := client.TempCopy().rooms

				// Check if room is valid and is subscribed
				if _, ok := rooms[room]; ok {
					rooms[room].BroadcastGmsg(message.Val)
				}
			}

		// Single room
		case any:
			// Check if room is valid and is subscribed
			rooms := client.TempCopy().rooms
			if _, ok := rooms[message.Rooms]; ok {
				rooms[message.Rooms].BroadcastGmsg(message.Val)
			}
		}

	case "pmsg":
		// Require username to be set before usage
		if client.RequireIDBeingSet(message) {
			return
		}

		rooms := TempCopyRooms(client.rooms)
		log.Printf("Searching for ID %s", message.ID)
		for _, room := range rooms {
			switch message.ID.(type) {
			case []interface{}:
				for _, multiquery := range message.ID.([]interface{}) {
					log.Printf("Room: %s - Multi query entry: %s, Result: %s", room.name, multiquery, room.FindClient(multiquery))
				}

			default:
				log.Printf("Room: %s - Result: %s", room.name, room.FindClient(message.ID))
			}
		}

	case "setid":
		// Val datatype validation
		switch message.Val.(type) {
		case string:
		case int64:
		case float64:
		case bool:
		default:
			// Send status code
			UnicastMessage(client, &PacketUPL{
				Cmd:      "statuscode",
				Code:     "E:102 | Datatype",
				CodeID:   102,
				Details:  "Username value (val) must be a string, boolean, float, or int",
				Listener: message.Listener,
			})
			return
		}

		// Prevent changing usernames
		if client.HandleIDSet(message) {
			return
		}

		// Update client attributes
		client.Lock()
		client.username = message.Val
		client.Unlock()

		// Use default room
		rooms := client.TempCopy().rooms
		for _, room := range rooms {
			room.BroadcastUserlistEvent("add", client, true)
			UnicastMessage(client, &PacketUPL{
				Cmd:   "ulist",
				Mode:  "set",
				Val:   room.GenerateUserList(),
				Rooms: room.name,
			})
		}

		// Send status code
		UnicastMessage(client, &PacketUPL{
			Cmd:      "statuscode",
			Code:     "I:100 | OK",
			CodeID:   100,
			Val:      client.GenerateUserObject(),
			Listener: message.Listener,
		})

	case "gvar":
		// Handle multiple types for room
		switch message.Rooms.(type) {

		// Value not specified in message
		case nil:
			// Use all subscribed rooms
			rooms := client.TempCopy().rooms
			for _, room := range rooms {
				room.BroadcastGvar(message.Name, message.Val)
			}

		// Multiple rooms
		case []any:
			// Use specified rooms
			for _, room := range message.Rooms.([]any) {
				rooms := client.TempCopy().rooms

				// Check if room is valid and is subscribed
				if _, ok := rooms[room]; ok {
					rooms[room].BroadcastGvar(message.Name, message.Val)
				}
			}

		// Single room
		case any:
			// Check if room is valid and is subscribed
			rooms := client.TempCopy().rooms
			if _, ok := rooms[message.Rooms]; ok {
				rooms[message.Rooms].BroadcastGvar(message.Name, message.Val)
			}
		}

	case "pvar":
		// Require username to be set before usage
		if !client.RequireIDBeingSet(message) {
			return
		}

	case "link":
		// Require username to be set before usage
		if !client.RequireIDBeingSet(message) {
			return
		}

		// Detect if single or multiple rooms
		switch message.Val.(type) {

		case nil:
			UnicastMessage(client, &PacketUPL{
				Cmd:     "statuscode",
				Code:    "E:101 | Syntax",
				CodeID:  101,
				Details: "Message missing required val key",
			})
			return

		// Multiple rooms
		case []interface{}:
			// Validate datatypes of array
			for _, elem := range message.Val.([]interface{}) {
				switch elem.(type) {
				case string:
				case int64:
				case float64:
				case bool:
				default:
					// Send status code
					UnicastMessage(client, &PacketUPL{
						Cmd:      "statuscode",
						Code:     "E:102 | Datatype",
						CodeID:   102,
						Details:  "Multiple rooms value (val) must be an array of strings, bools, floats, or ints.",
						Listener: message.Listener,
					})
					return
				}
			}
			// Subscribe to all rooms
			for _, name := range message.Val.([]interface{}) {

				// Create room if it doesn't exist
				room := client.manager.CreateRoom(name)

				// Add the client to the room
				room.SubscribeClient(client)
			}

		// Single room
		case interface{}:
			// Validate datatype
			switch message.Val.(type) {
			case string:
			case int64:
			case float64:
			case bool:
			default:
				// Send status code
				UnicastMessage(client, &PacketUPL{
					Cmd:      "statuscode",
					Code:     "E:102 | Datatype",
					CodeID:   102,
					Details:  "Single room value (val) must be a string, boolean, float, int.",
					Listener: message.Listener,
				})
				return
			}

			// Subscribe to single room
			// Create room if it doesn't exist
			room := client.manager.CreateRoom(message.Val)

			// Add the client to the room
			room.SubscribeClient(client)
		}

		// Send status code
		UnicastMessage(client, &PacketUPL{
			Cmd:    "statuscode",
			Code:   "I:100 | OK",
			CodeID: 100,
		})

	case "unlink":
		// Require username to be set before usage
		if !client.RequireIDBeingSet(message) {
			return
		}
		// Detect if single or multiple rooms
		switch message.Val.(type) {

		case nil:
			// Unsubscribe all rooms and rejoin default
			rooms := client.TempCopy().rooms
			for _, room := range rooms {
				room.UnsubscribeClient(client)
				// Destroy room if empty, but don't destroy default room
				if len(room.clients) == 0 && (room.name != "default") {
					client.manager.DeleteRoom(room.name)
				}
			}

			// Get default room
			defaultroom := client.manager.CreateRoom("default")

			// Add the client to the room
			defaultroom.SubscribeClient(client)

		// Multiple rooms
		case []interface{}:
			// Validate datatypes of array
			for _, elem := range message.Val.([]interface{}) {
				switch elem.(type) {
				case string:
				case bool:
				case int64:
				case float64:
				default:
					// Send status code
					UnicastMessage(client, &PacketUPL{
						Cmd:      "statuscode",
						Code:     "E:102 | Datatype",
						CodeID:   102,
						Details:  "Multiple rooms value (val) must be an array of strings",
						Listener: message.Listener,
					})
					return
				}
			}

			// Get currently subscribed rooms
			rooms := client.TempCopy().rooms

			// Validate room and verify that it was joined
			for _, _room := range message.Val.([]interface{}) {
				if _, ok := rooms[_room]; ok {
					room := rooms[_room]
					room.UnsubscribeClient(client)
					// Destroy room if empty, but don't destroy default room
					if len(room.clients) == 0 && (room.name != "default") {
						client.manager.DeleteRoom(room.name)
					}
				}
			}

		// Single room
		case interface{}:
			// Validate datatype
			switch message.Val.(type) {
			case string:
			case bool:
			case int64:
			case float64:
			default:
				// Send status code
				UnicastMessage(client, &PacketUPL{
					Cmd:      "statuscode",
					Code:     "E:102 | Datatype",
					CodeID:   102,
					Details:  "Single room value (val) must be a string",
					Listener: message.Listener,
				})
				return
			}

			// Get currently subscribed rooms
			rooms := client.TempCopy().rooms

			// Validate if room is joined and remove client
			if _, ok := rooms[message.Val]; ok {
				room := rooms[message.Val]
				room.UnsubscribeClient(client)
				// Destroy room if empty, but don't destroy default room
				if len(room.clients) == 0 && (room.name != "default") {
					client.manager.DeleteRoom(room.name)
				}
			}
		}

		// Send status code
		UnicastMessage(client, &PacketUPL{
			Cmd:    "statuscode",
			Code:   "I:100 | OK",
			CodeID: 100,
		})

	case "direct":
		// Require username to be set before usage
		if !client.RequireIDBeingSet(message) {
			return
		}

	case "echo":
		UnicastMessage(client, message)

	default:
		// Handle unknown commands
		UnicastMessage(client, &PacketUPL{
			Cmd:      "statuscode",
			Code:     "E:109 | Invalid command",
			CodeID:   109,
			Val:      client.GenerateUserObject(),
			Listener: message.Listener,
		})
	}
}

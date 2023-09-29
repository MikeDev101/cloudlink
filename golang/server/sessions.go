package cloudlink

import (
	"log"

	"github.com/goccy/go-json"

	"github.com/gofiber/contrib/websocket"
)

func (client *Client) CloseWithMessage(statuscode int, closeMessage string) {
	client.connection.WriteMessage(
		websocket.CloseMessage,
		websocket.FormatCloseMessage(
			statuscode,
			closeMessage,
		),
	)
	client.connection.Close()
}

func (client *Client) MessageHandler(manager *Manager) {
	// websocket.Conn bindings https://pkg.go.dev/github.com/fasthttp/websocket?tab=doc#pkg-index
	var (
		_       int
		message []byte
		err     error
	)
	for {
		// Listen for new messages
		if _, message, err = client.connection.ReadMessage(); err != nil {
			break
		}

		switch client.protocol {
		case 0: // Detect protocol
			// CL4 protocol
			var cl4packet PacketUPL
			if err := json.Unmarshal([]byte(message), &cl4packet); err != nil {
				client.CloseWithMessage(websocket.CloseUnsupportedData, "JSON parsing error")
			}

			// Scratch protocol
			var scratchpacket Scratch
			if err := json.Unmarshal([]byte(message), &scratchpacket); err != nil {
				client.CloseWithMessage(websocket.CloseUnsupportedData, "JSON parsing error")
			}

			// Handle requests
			if cl4packet.Cmd != "" {
				CL4ProtocolDetect(client)
				CL4MethodHandler(client, &cl4packet)
			} else if scratchpacket.Method != "" {
				ScratchProtocolDetect(client)
				ScratchMethodHandler(client, &scratchpacket)
			} else {
				client.CloseWithMessage(websocket.CloseProtocolError, "Couldn't identify protocol")
			}

		case 1: // CL4
			var cl4packet PacketUPL
			if err := json.Unmarshal([]byte(message), &cl4packet); err != nil {
				client.CloseWithMessage(websocket.CloseUnsupportedData, "JSON parsing error")
			}
			CL4MethodHandler(client, &cl4packet)

		case 2: // Scratch
			var scratchpacket Scratch
			if err := json.Unmarshal([]byte(message), &scratchpacket); err != nil {
				client.CloseWithMessage(websocket.CloseUnsupportedData, "JSON parsing error")
			}
			ScratchMethodHandler(client, &scratchpacket)
		}
	}
}

// SessionHandler is the root function that makes CloudLink work. As soon as a client request gets upgraded to the websocket protocol, this function should be called.
func SessionHandler(con *websocket.Conn, manager *Manager) {
	/*
		// con.Locals is added to the *websocket.Conn
		log.Println(con.Locals("allowed"))  // true
		log.Println(con.Params("id"))       // 123
		log.Println(con.Query("v"))         // 1.0
		log.Println(con.Cookies("session")) // ""
	*/

	// Register client
	client := NewClient(con, manager)
	manager.AddClient(client)

	// Log IP address of client (if enabled)
	if manager.Config.CheckIPAddresses {
		log.Printf("[%s] Client %s (%s) IP address: %s", manager.name, client.id, client.uuid, con.RemoteAddr().String())
	}

	// Remove client from manager once the session has ended
	defer manager.RemoveClient(client)

	// Begin handling messages throughout the lifespan of the connection
	client.MessageHandler(manager)
}

package cloudlink

import (
	"sync"

	"github.com/bwmarrin/snowflake"
	"github.com/gofiber/contrib/websocket"
	"github.com/google/uuid"
)

// The client struct serves as a template for handling websocket sessions. It stores a client's UUID, Snowflake ID, manager and websocket connection pointer(s).
type Client struct {
	connection      *websocket.Conn
	connectionMutex sync.RWMutex
	manager         *Manager
	id              snowflake.ID
	uuid            uuid.UUID
	username        interface{}
	protocol        uint8 // 0 - Unset, 1 - CL4, 2 - Scratch
	rooms           map[interface{}]*Room
	handshake       bool

	// Lock state for rooms
	sync.RWMutex
}

package main

import (
	"log"
	"runtime/debug"
	"time"

	"github.com/gofiber/contrib/websocket"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/monitor"

	cloudlink "github.com/mikedev101/cloudlink/golang/server"
)

func main() {
	// Configure runtime settings
	debug.SetGCPercent(35) // 35% limit for GC

	// Create fiber application
	app := fiber.New()

	// Create CloudLink server
	manager := cloudlink.New("root")

	// Modify configuration of the CloudLink manager
	manager.Config.CheckIPAddresses = false
	manager.Config.EnableMOTD = true
	manager.Config.MOTDMessage = "CloudLink Golang using Gofiber!"

	// Add a websocket path
	app.Use("/ws", func(c *fiber.Ctx) error {
		// IsWebSocketUpgrade returns true if the client
		// requested upgrade to the WebSocket protocol.
		if websocket.IsWebSocketUpgrade(c) {
			// c.Locals("allowed", true)
			return c.Next()
		}
		return fiber.ErrUpgradeRequired
	})

	// Bind CloudLink server to websocket path
	app.Get("/ws", websocket.New(func(client *websocket.Conn) {
		cloudlink.SessionHandler(client, manager)
	}))

	app.Get("/monitor", monitor.New(
		monitor.Config{
			Title:   "CloudLink Metrics",
			Refresh: (50 * time.Millisecond),
		},
	))

	log.Fatal(app.Listen(":3000"))
	// Access the websocket server: ws://0.0.0.0:3000/

	//log.Fatal(app.ListenTLS("0.0.0.0:3000", "./cert.pem", "./key.pem"))
	// Access the websocket server: wss://0.0.0.0:3000/
}

from fastapi import FastAPI, WebSocket
import random
import uvicorn

# Create application
app = FastAPI(title='WebSocket Example')

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            # Wait for any message from the client
            message = await websocket.receive_text()
            print(message)
            # echo
            await websocket.send_text(message)
        except Exception as e:
            print('error:', e)
            break

if __name__ == "__main__":
	uvicorn.run(app, port=3001, log_level="debug")
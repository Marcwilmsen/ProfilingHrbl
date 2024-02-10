import asyncio
import websockets
import json

connected_clients = set()


async def register(websocket):
    connected_clients.add(websocket)


async def unregister(websocket):
    connected_clients.remove(websocket)


async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])


async def websocket_handler(websocket, path):
    await register(websocket)
    try:
        async for message in websocket:
            pass  # Here, you can handle incoming messages if needed
    finally:
        await unregister(websocket)


async def http_handler(request):
    if request.method == 'POST':
        data = await request.json()
        await broadcast(json.dumps(data))
        confirmation = json.dumps({"status": "success", "message": data})
        return websockets.Response(status=200, body=confirmation, content_type='application/json')
    return websockets.Response(status=405)


start_server = websockets.serve(websocket_handler, "localhost", 6789)
http_server = websockets.serve(
    http_handler, "localhost", 6790, create_protocol=websockets.HTTPProtocol)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_until_complete(http_server)
asyncio.get_event_loop().run_forever()

from threading import Lock
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync  # Importing async_to_sync
import json

class ConsoleConsumer(WebsocketConsumer):
    active_connections = set()  # Define the active_connections set
    _connections_lock = Lock()  # Lock for managing active_connections

    def connect(self):
        self.accept()
        self.group_name = "notification_group"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        with ConsoleConsumer._connections_lock:
            ConsoleConsumer.active_connections.add(self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        with ConsoleConsumer._connections_lock:
            ConsoleConsumer.active_connections.discard(self.channel_name)

    def group_message(self, event):
        message = event['text']
        self.send(text_data=message)

    # Handler for "websocket.send" message type
    def websocket_send(self, event):
        message = event['text']
        self.send(text_data=message)
        print("send message to frontend: ", message)

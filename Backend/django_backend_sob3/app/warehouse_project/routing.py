# warehouse_project/routing.py

from warehouse_project import consumer
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
# assuming your consumers.py is in the warehouse_project directory


websocket_urlpatterns = [
    path('ws/console/', consumer.ConsoleConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})


websocket_urlpatterns = [
    # Replace 'some_path' with your WebSocket path
    re_path(r'ws/console/$', consumer.ConsoleConsumer.as_asgi()),
]

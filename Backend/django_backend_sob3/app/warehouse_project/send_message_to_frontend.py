import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from warehouse_project.consumer import ConsoleConsumer
import logging
# def send_message_to_session(session_key, message):
#     channel_layer = get_channel_layer()
#     channel_name = ConsoleConsumer.connected_channels.get(session_key)
#     if channel_name:
#         async_to_sync(channel_layer.send)(channel_name, {
#             "type": "websocket.send",
#             "text": json.dumps(message),
#         })


logger = logging.getLogger(__name__)
def send_message_to_all(message):
    print("in send message func with message: ", message)
    channel_layer = get_channel_layer()
    text_message = json.dumps(message)
    try:
        async_to_sync(channel_layer.group_send)(
            "notification_group", {
                "type": "group.message",
                "text": text_message
            }
        )
        logger.info(f"Message sent to group: {text_message}")
    except Exception as e:
        logger.error(f"Error sending message to group: {e}")

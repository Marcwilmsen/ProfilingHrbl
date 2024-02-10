# logging_handlers.py
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class WebSocketLoggingHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('console_group', {
            'type': 'console_message',
            'message': log_entry
        })

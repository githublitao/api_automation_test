# -*- coding: utf-8 -*-

# @Author  : litao

# @Project : api_automation_test

# @FileName: consumers.py

# @Software: PyCharm
# chat/consumers.py
import time

from asgiref.sync import async_to_sync
from channels.generic.websocket import  WebsocketConsumer
import json

from RootDirectory import PROJECT_PATH


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        self.token_group_name = 'chat_%s' % self.token

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.token_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.token_group_name,
            self.channel_name
        )
    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['log']
        async_to_sync(self.channel_layer.group_send)(
            self.token_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'index': text_data_json.get('index')
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        # text_data_json = json.loads(text_data)
        message = event['message']
        log_length = 0
        end_data = ''
        while True:
            with open(PROJECT_PATH+message, 'r', encoding='UTF-8') as f:
                contents = f.readlines()
                length_tmp = len(contents)
            if end_data != contents[log_length-1] and log_length > 0:
                log_length = log_length - 1
            for i in range(log_length, length_tmp):
                if event.get('index') or event.get('index') == 0:
                    data = {
                        'index': event.get('index'),
                        'message': contents[i],
                        "line": i
                }
                else:
                    data = {
                        'message': contents[i],
                        "line": i
                    }
                self.send(text_data=json.dumps(data))
                # await req.websocket.send(contents[i].encode('utf-8'))
            log_length = length_tmp
            end_data = contents[length_tmp-1]
            time.sleep(1)
            if len(contents) > 0:
                if contents[length_tmp-1] in ['Finish', 'End']:
                    break

from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
import json
from .models import *

class RoomConsumer(WebsocketConsumer):
    # Connect user to group
    def connect(self):
        self.user = self.scope['user']
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group = get_object_or_404(ChatGroup, groupName=self.group_name)
        
        # Add user to group channel layer method
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )
        
        self.accept()
        
    # Disconnect user from group
    def disconnect(self, close_code):
        # Remove user from group channel layer method
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
        
    
    # Receive message on group
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        
        # Create message instance and populate its fields
        message = ChatMessage.objects.create(
            body = body,
            author = self.user,
            group = self.group
        )
        # Create event dictionary
        event = {
            'type': 'message_handler',
            'message_id': message.id
        }
        # Send text data to all open connections
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, event
        )
        
        
    def message_handler(self, event):
        message_id = event['message_id']
        message = ChatMessage.objects.get(id=message_id)
        # Create context dictionary
        context = {
            'message': message,
            'author': self.user
        }
        # Send text data to front end
        html = render_to_string("chat/partials/chat_message_partial.html", context=context)
        self.send(text_data=html)
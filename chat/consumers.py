from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import json
from .models import *

class RoomConsumer(WebsocketConsumer):
    # Connect user to group
    def connect(self):
        self.user = self.scope['user']
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group = get_object_or_404(ChatGroup, groupName=self.group_name)
        self.accept()
    
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
        
        # Create context
        context = {
            'message': message,
            'author': self.user
        }
        # Send text data to front end
        html = render_to_string("chat/partials/chat_message_partial.html", context=context)
        self.send(text_data=html)
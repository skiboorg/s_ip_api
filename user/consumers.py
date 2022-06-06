import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import User
from channels.db import database_sync_to_async

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class UserOnline(AsyncWebsocketConsumer):
    user = None

    async def connect(self):
        self.room_name = 'users'
        self.room_group_name = 'users'
        # print(self.room_name)
        # print(self.room_group_name)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        # print(self.user)
        await self.channel_layer.group_discard(
            'users',
            self.channel_name
        )
        await self.set_user_offline()

    @database_sync_to_async
    def set_user_offline(self):
        self.user.channel = None
        self.user.is_online = False
        self.user.save(update_fields=["is_online","channel"])
        return


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get('user_id'):
            self.user = await self.get_user(text_data_json['user_id'])
            # print(self.user)
            await self.channel_layer.group_add("users", self.channel_name)
            # print(f"Added {self.channel_name} channel to users")
            await self.save_user_channel()
            # channel_layer = get_channel_layer()
            # await channel_layer.send(self.channel_name, {
            #     "type": "user.notify",
            #
            # })
        if text_data_json.get('logout_id'):
            await self.disconnect(1)

    @database_sync_to_async
    def save_user_channel(self):
        self.user.channel = self.channel_name
        self.user.is_online = True
        self.user.save(update_fields=["is_online", "channel"])
        return

    @database_sync_to_async
    def get_user(self,id):
        return User.objects.get(id=id)

    async def user_notify(self, event):
        # Handles the "chat.message" event when it's sent to us.
        message = event['message']
        type = event['event']
        # url = event['url']
        event_id = event['event_id']
        await self.send(text_data=json.dumps({
             'event': type,
             'message': message,
             # 'url': url,
             'event_id': event_id,

         }))
    # async def chat_message(self, event):
    #     message = event['message']
    #
    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))


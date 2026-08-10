import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message
@database_sync_to_async
def save_message(room_id,user,message):
    print("SAVING MESSAGE:",room_id,user,message)
    conversation = Conversation.objects.get(id=room_id)
    return Message.objects.create(conversation=conversation,sender=user,text=message)
class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        print("USER:",self.scope["user"])
        print("AUTHENTICATED:",self.scope["user"].is_authenticated  )
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print("Connected room:", self.room_id)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
     print("========== RECEIVE START ==========")

     try:
        data = json.loads(text_data)
        message = data["message"]

        print("Message received:", message)

        user = self.scope.get("user")

        print("USER FROM SCOPE:", user)

        if user is None or not user.is_authenticated:
            print("USER IS NOT AUTHENTICATED")
            return

        print("Sender:", user)
        print("Authenticated:", user.is_authenticated)

        saved_message = await save_message(
            self.room_id,
            user,
            message
        )

        print("MESSAGE SAVED:", saved_message.id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message
            }
        )

        print("MESSAGE SENT TO GROUP")

     except Exception as e:
        print("RECEIVE ERROR:", repr(e))
 
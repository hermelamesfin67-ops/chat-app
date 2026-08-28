import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message

from django.utils import timezone
from django.contrib.auth import get_user_model


@database_sync_to_async
def save_message(room_id, user, text):
    # print("SAVING MESSAGE:",room_id,user,text)
    conversation = Conversation.objects.get(id=room_id)
    saved = Message.objects.create(
        conversation=conversation, sender=user, text=text)
    return {
        "id": saved.id,
        "conversation_id": saved.conversation.id,
        "sender_id": saved.sender.id,
        "text": saved.text

    }


User = get_user_model()


@database_sync_to_async
def update_online_status(user_id, is_online):
    user = User.objects.get(id=user_id)

    print("USER:", user.username)
    print("BEFORE:", user.is_online, user.last_seen)

    user.is_online = is_online

    if not is_online:
        user.last_seen = timezone.now()

    user.save()

    print("AFTER:", user.is_online, user.last_seen)


class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def check_participant(self, room_id, user_id):
        return Conversation.objects.filter(
            id=room_id,
            participants__id=user_id
        ).exists()

    async def connect(self):
        self.room_id = int(
            self.scope["url_route"]["kwargs"]["room_id"]
        )
        self.room_group_name = f"chat_{self.room_id}"

        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        is_participant = await self.check_participant(
            self.room_id,
            user.id
        )
        print("ROOM:", self.room_id)

        print("USER ID:", user.id)
        print("IS PARTICIPANT:", is_participant)
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await update_online_status(user.id, True)

        print(
            f"User {user.username} connected to room {self.room_id}"
        )

    async def disconnect(self, close_code):
        print("========== DISCONNECT ==========")
        print("CLOSE CODE:", close_code)

        user = self.scope["user"]

        if user.is_authenticated:
            await update_online_status(user.id, False)

        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        print("========== RECEIVE START ==========")

        try:
            data = json.loads(text_data)
            text = data["text"]

            print("Message received:", text)

            user = self.scope.get("user")

            print("USER FROM SCOPE:", user)

            if user is None or not user.is_authenticated:
                print("USER IS NOT AUTHENTICATED")
                return

            print("Sender:", user)
            # print("Authenticated:", user.is_authenticated)

            saved_message = await save_message(
                self.room_id,
                user,
                text
            )

            print("MESSAGE SAVED:", saved_message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": saved_message
                }
            )

        except Exception as e:
            print("RECEIVE ERROR:", repr(e))

    async def chat_message(self, event):

        message = event["message"]
        await self.send(
            text_data=json.dumps(message)
        )

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
        "message_id": str(saved.id),
        "conversation_id": str(saved.conversation.id),
        "sender": {
            "username": saved.sender.username,
            "email": saved.sender.email,
            "phone_number": saved.sender.phone_number,
            "profile_picture": "",
        },
        "text": saved.text,
        "created_at": saved.created_at.isoformat(),
        "is_read": saved.is_read,
        "message_type": saved.message_type,
    }

User = get_user_model()


@database_sync_to_async
def update_online_status(user_id, is_online):
    user = User.objects.get(id=user_id)

    # print("USER:", user.username)
    # print("BEFORE:", user.is_online, user.last_seen)

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

        print("========== CONNECT ==========")
        print("USER:", user)
        print("ROOM ID:", self.room_id)
        print("ROOM GROUP NAME:", self.room_group_name)

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
        print("========== GROUP ADD ==========")
        print("USER:", user.username)
        print("CHANNEL:", self.channel_name)
        print("GROUP:", self.room_group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print("GROUP ADD DONE")

        await self.accept()
        await update_online_status(user.id, True)
        await self.mark_messages_as_read()

        print(
            f"User {user.username} connected to room {self.room_id}"
        )

    @database_sync_to_async
    def mark_messages_as_read(self):
        Message.objects.filter(
            conversation_id=self.room_id,
            is_read=False
        ).exclude(
            sender=self.scope["user"]
        ).update(
            is_read=True
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
            print("RAW:", text_data)

            data = json.loads(text_data)
            text = data["text"]

            print("TEXT:", text)

            user = self.scope["user"]
            print("USER:", user)

            saved_message = await save_message(
                self.room_id,
                user,
                text
            )

            print("1️⃣ SAVED:", saved_message)

            print("2️⃣ GROUP:", self.room_group_name)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": saved_message,
                }
            )

            print("3️⃣ GROUP SEND FINISHED")

        except Exception as e:
            print("❌ RECEIVE ERROR:", repr(e))

            import traceback
            traceback.print_exc()


    async def chat_message(self, event):
        print("========== CHAT MESSAGE ==========")

        try:
            print("USER:", self.scope["user"])
            print("EVENT:", event)

            await self.send(
                text_data=json.dumps(event["message"])
            )

            print("✅ SENT TO:", self.scope["user"])

        except Exception as e:
            print("❌ CHAT MESSAGE ERROR:", repr(e))

            import traceback
            traceback.print_exc()

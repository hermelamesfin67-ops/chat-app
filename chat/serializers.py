from django.db.models import Count
from .models import Conversation, Message
from rest_framework import serializers
from .models import Conversation, Message, User

from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer)
from django.contrib.auth import authenticate


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'phone_number'

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        if phone_number.startswith("09"):
            phone_number = '+251' + phone_number[1:]
        elif not phone_number.startswith("+251"):
            raise serializers.ValidationError(
                "Invalid phone number"
            )
        user = authenticate(username=phone_number, password=password)
        if user is None:
            raise serializers.ValidationError(
                'Invalid phone number or password'
            )
        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
                "profile_picture": (user.profile_picture.url
                                    if user.profile_picture
                                    else None)
            }
        }


class UserSignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=6
    )

    confirm_password = serializers.CharField(
        write_only=True
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone_number",
            "password",
            "confirm_password",
            "profile_picture",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs

    def validate_phone_number(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain only numbers."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must be 10 digits."
            )

        if not value.startswith("09"):
            raise serializers.ValidationError(
                "Phone number must start with 09."
            )

    # Check the same format that will be stored by UserManager
        formatted_phone = "+251" + value[1:]

        if User.objects.filter(phone_number=formatted_phone).exists():
            raise serializers.ValidationError(
                "Phone number already exists."
            )

        return value

    def create(self, validated_data):
        print("CREATE IS RUNNING!")

        validated_data.pop("confirm_password")
        print("PHONE BEFORE CREATE:", validated_data["phone_number"])

        user = User.objects.create_user(
            **validated_data
        )

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username',  'profile_picture', 'bio',
                  'email', 'phone_number',
                  'role', 'is_online', 'last_seen']
        read_only_fields = ['is_online', 'last_seen', 'phone_number', 'role']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSignupSerializer(read_only=True)
    message_id = serializers.IntegerField(source='id', read_only=True)
    conversation_id = serializers.IntegerField()

    class Meta:
        model = Message
        fields = ('message_id', 'conversation_id', 'sender',
                  'text', 'created_at', 'is_read', 'message_type')

    def create(self, validated_data):
        request = self.context['request']

        message = Message.objects.create(
            sender=request.user,
            **validated_data
        )

        return message

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance


class ChatListSerializer(serializers.ModelSerializer):

    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    conversation_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "other_user",
            
            "last_message",
            "created_at",
        ]

    def get_other_user(self, obj):
        request = self.context["request"]

        other_user = obj.participants.exclude(
            id=request.user.id
        ).first()

        if not other_user:
            return None

        return {
                    "id": other_user.id,
                    "name": other_user.username,
                    "profile": other_user.profile_picture.url if other_user.profile_picture else None,
                    "status": other_user.is_online,
                    "last_seen": other_user.last_seen,
                }
        

    def get_last_message(self, obj):
        message = obj.messages.order_by("-created_at").first()

        if not message:
            return ""

        return message.text


class ConversationSerializer(serializers.ModelSerializer):
    conversation_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Conversation
        fields = ("conversation_id", "participants", "created_at")

    def create(self, validated_data):
        participants = validated_data.pop("participants")

        conversation = (
            Conversation.objects
            .filter(participants__in=participants)
            .annotate(participant_count=Count("participants", distinct=True))
            .filter(participant_count=2)
            .first()
        )

        if conversation:
            existing_participants = set(
                conversation.participants.values_list("id", flat=True)
            )
            new_participants = set(
                user.id for user in participants
            )

            if existing_participants == new_participants:
                return conversation

        # No existing conversation → create one
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.add(*participants)

        return conversation


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number',
                  'profile_picture', 'last_seen']


class UserSearchSerializers(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(read_only=True)
    is_online = serializers.BooleanField(read_only=True)
    last_seen = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture',
                  'last_seen', 'is_online']
        ordered_by = '-last_seen'


# class ForgetPasswordSerializers(serializers.Serializer):
#     username = serializers.CharField()
#     email = serializers.EmailField()
#     phone_number = serializers.CharField()
class ChatRoomSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    conversation_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'other_user', 'created_at']

    def get_other_user(self, obj):
        request = self.context["request"]
        other_user = obj.participants.exclude(
            id=request.user.id
        ).first()

        if not other_user:
            return None

        return {
            "id": other_user.id,
            "name": other_user.username,
            "profile": other_user.profile_picture.url if other_user.profile_picture else None,
            "status": other_user.is_online,
            "last_seen": other_user.last_seen,
        }

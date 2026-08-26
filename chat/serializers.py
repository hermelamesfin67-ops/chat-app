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

    class Meta:
        model = User
        fields = [
            "username",
            "phone_number",
            "password",
            "confirm_password",
            "profile_picture"
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs

    def validate_phone_number(self, value):
      if value.startswith("0"):
        value = "+251" + value[1:]
        return value
      
    def validate_phone_number(self, value):

      if User.objects.filter(phone_number=value).exists():
        raise serializers.ValidationError(
            "Phone number already exists."
        )

      return value
     

    def create(self, validated_data):
        print("CREATE IS RUNNING!")

        validated_data.pop("confirm_password")

        user = User.objects.create_user(
            **validated_data
        )

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username',  'profile_picture', 'bio',
                  'id', 'phone_number',
                  'role', 'is_online', 'last_seen']
        read_only_fields = ['is_online', 'last_seen', 'phone_number', 'role']


class MessageSerializer(serializers.ModelSerializer):
    # sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender',
                  'text', 'created_at', 'is_read', 'message_type')

    def create(self, validated_data):
        participants = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data
                                                   )
        conversation.participants.set(*participants
                                      )
        return conversation

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance


class ChatListSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "user",
            "last_message",
            "created_at",
        ]

    def get_user(self, obj):
        request = self.context["request"]
        current_user = request.user

        other_user = obj.participants.exclude(
            id=current_user.id
        ).first()

        if not other_user:
            return None

        return {
            "id": other_user.id,
            "name": other_user.username,
            "avatar": None,
        }

    def get_last_message(self, obj):
        message = obj.messages.order_by("-created_at").first()

        if not message:
            return ""

        return message.text


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'created_at')

    def create(self, validated_data):
        participants = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.add(*participants)

        return conversation

    def update(self, instance, validated_data):
        participants = validated_data.pop('participants')
        instance.participants.set(participants)
        return super().update(instance, validated_data)
class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'profile_picture'] 

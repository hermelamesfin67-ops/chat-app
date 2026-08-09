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

    def create(self, validated_data):
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
        read_only_fields=['is_online', 'last_seen', 'phone_number', 'role']





class MessageSerializer(serializers.ModelSerializer):
    # sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender',
                  'content', 'created_at', 'is_read', 'message_type')

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

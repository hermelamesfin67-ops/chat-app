from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender',
                  'content', 'created_at', 'is_read')

    def create(self, validated_data):
        conversation = validated_data.pop('conversation')
        message = Message.objects.create(**validated_data)
        message.conversation = conversation
        message.save()
        return message

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

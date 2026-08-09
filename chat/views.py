from django.shortcuts import render
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, PhoneTokenObtainPairSerializer, UserSignupSerializer, ProfileSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import (TokenObtainPairView
                                            )
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()


class PhoneLoginView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer
class ProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user


class ConversationListCreateView(ListCreateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)
    permission_classes = [IsAuthenticated]


class UserSignUpView(CreateAPIView):
    serializer_class = UserSignupSerializer




class ConversationDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer


class MessageListCreateView(ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
  #  permission_classes = [IsAuthenticated]

   # def perform_create(self, serializer):
    #   serializer.save(sender=self.request.user)


class MessageDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


# Create your views here.
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )

        except Exception:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )

def websocket_test(request):
    return render(request, "chat/text.html")

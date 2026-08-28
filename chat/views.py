from django.shortcuts import render
from .models import Conversation, Message
from .serializers import (ConversationSerializer, MessageSerializer,
                          PhoneTokenObtainPairSerializer, UserSignupSerializer,
                          ProfileSerializer, UserSerializers, ChatListSerializer,
                          UserSearchSerializers, ChatRoomSerializer)
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import (TokenObtainPairView
                                            )
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
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

    # def get_queryset(self):
    # return Conversation.objects.filter(participants=self.request.user)
#    permission_classes = [IsAuthenticated]


class UserSignUpView(CreateAPIView):
    serializer_class = UserSignupSerializer


class UsersDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers


class UserSearch(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response([])

        users = User.objects.filter(
            username__icontains=query
        ).exclude(
            id=request.user.id
        )[:10]

        serializer = UserSearchSerializers(
            users,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


class ConversationDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user not in instance.participants.all():
            raise PermissionDenied(
                "You are not a participant in this conversation."
            )

        instance.delete()

        return Response(
            {
                "success": True,
                "message": "Conversation deleted successfully."
            },
            status=status.HTTP_200_OK
        )


class MessageListCreateView(ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.request.query_params.get("conversation")

        return Message.objects.filter(
            conversation_id=conversation_id
        ).order_by("created_at")


class MessageDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(
            conversation__participants=self.request.user
        )

    def perform_update(self, serializer):
        message = self.get_object()

        if message.sender != self.request.user:
            raise PermissionDenied(
                "You can only edit your own messages."
            )

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.sender != request.user:
            raise PermissionDenied(
                "You can only delete your own messages."
            )

        instance.delete()

        return Response(
            {
                "success": True,
                "message": "Message deleted successfully."
            },
            status=status.HTTP_200_OK
        )


class ChatListView(ListCreateAPIView):
    serializer_class = ChatListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print("self", self.request)

        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            "participants",
            "messages",
        ).order_by("-created_at")


class Chat_RoomListView(ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related("participants")

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



    
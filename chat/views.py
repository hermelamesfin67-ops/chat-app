from django.utils import timezone
import random
from .email_utils import send_otp_email
from django.shortcuts import render
from .models import Conversation, Message, PasswordOtpRest
from .serializers import (ConversationSerializer, MessageSerializer,
                          PhoneTokenObtainPairSerializer, UserSignupSerializer,
                          ProfileSerializer, UserSerializers, ChatListSerializer,
                          UserSearchSerializers, ChatRoomSerializer, ForgotPasswordSerializer,
                          VerifyOTPSerializer,
                          ResetPasswordSerializer,
                          ChangePasswordSerializer,
                          )
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
from django.core import signing
from rest_framework.permissions import AllowAny
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
        user = self.request.user

        conversation_id = self.request.query_params.get("conversation")

        queryset = Conversation.objects.filter(
            participants=user
        )

        if conversation_id:
            queryset = queryset.filter(id=conversation_id)

        return queryset


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


User = get_user_model()


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        serializer = ForgotPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        if phone_number.startswith("0"):
            phone_number = "+251" + phone_number[1:]

        try:
            user = User.objects.get(
                phone_number=phone_number
            )

        except User.DoesNotExist:

            return Response(
                {
                    "message": "If the account exists, an OTP has been sent."
                },
                status=status.HTTP_200_OK
            )

        otp = str(random.randint(100000, 999999))

        PasswordOtpRest.objects.filter(
            user=user
        ).delete()

        PasswordOtpRest.objects.create(
            user=user,
            otp=otp
        )
        print("OTP:", otp)
        send_otp_email(user.email, otp)

        return Response(
            {
                "message": "If the account exists, an OTP has been sent.",
                "otp_expires_in": 300,
                "otp_expires_unit": "seconds"
            
            },
            status=status.HTTP_200_OK
        )
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        serializer = VerifyOTPSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        if phone_number.startswith("0"):
            phone_number = "+251" + phone_number[1:]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(
                phone_number=phone_number
            )

        except User.DoesNotExist:

            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            otp_record = PasswordOtpRest.objects.get(
                user=user
            )

        except PasswordOtpRest.DoesNotExist:

            return Response(
                {"error": "OTP not found. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_record.is_expired():

            otp_record.delete()

            return Response(
                {"error": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_record.otp != otp:

            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_record.is_verified = True
        otp_record.save(update_fields=["is_verified"])

        reset_token = signing.dumps(
            {"user_id": user.id},
            salt="password-reset"
        )

        return Response(
            {
                "message": "OTP verified successfully.",
                "access_token": reset_token
            },
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        serializer = ResetPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data["access_token"]
        new_password = serializer.validated_data["new_password"]

        try:
            data = signing.loads(
                access_token,
                salt="password-reset",
                max_age=900
            )

        except signing.SignatureExpired:

            return Response(
                {
                    "error": "Reset access token has expired. Please request a new OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except signing.BadSignature:

            return Response(
                {
                    "error": "Invalid reset access token."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(
                id=data["user_id"]
            )

        except User.DoesNotExist:

            return Response(
                {
                    "error": "Invalid request."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        PasswordOtpRest.objects.filter(
            user=user
        ).delete()

        return Response(
            {
                "message": "Password reset successfully."
            },
            status=status.HTTP_200_OK
        )
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = request.user
        

        old_password = serializer.validated_data[
         "old_password"
        ]

        new_password = serializer.validated_data[
        "new_password"
          ]

        if not user.check_password(old_password):
            return Response(
                {
                    "error": "old password is incorrect."
                },


                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()

        return Response(
            {
                "message": "Password changed successfully."
            },
            status=status.HTTP_200_OK
        )
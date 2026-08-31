from .views import websocket_test
from django.urls import path
from .views import (
    ConversationListCreateView,
    ConversationDetailView,
    MessageListCreateView,
    MessageDetailView,
    PhoneLoginView,
    UserSignUpView,
    ProfileView,
    LogoutView,
    UserSearch,
    ChatListView,
    UsersDetailView, 
    UserListView,
    Chat_RoomListView,
    ForgotPasswordView,
    VerifyOTPView,
    ResetPasswordView,
    ChangePasswordView,
    TestLogView

)

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', PhoneLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='my-profile'),
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path("test/", websocket_test, name="test"),
    path('users/search/', UserSearch.as_view(), name='user-search'),
    path("chat-rooms/", Chat_RoomListView.as_view(), name='chat_rooms'),
    path("conversations/", ConversationListCreateView.as_view(), name='conversations'),
    path("conversations/<int:pk>/", ConversationDetailView.as_view(),
         name='conversation-detail'),
    path("test-log/", TestLogView.as_view(), name='test-log'),
    path("change-password/", ChangePasswordView.as_view(), name='change-password'),
    path("messages/", MessageListCreateView.as_view(), name='messages'),
    path("chats/", ChatListView.as_view(), name='chats'),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name='message-detail'),
    path("logout/", LogoutView.as_view(), name='logout'),
    path("users/<int:pk>/", UsersDetailView.as_view(), name='user-detail'),
    path('users/', UserListView.as_view(), name='user-list'),
    path( "forgot-password/",ForgotPasswordView.as_view(),name="forgot-password"),
    path("verify-otp/",VerifyOTPView.as_view(),name="verify-otp"),
    path( "reset-password/",ResetPasswordView.as_view(),name="reset-password" ),
]



# 💬 Chatty — Real-Time Chat Application
**real-time chat application** built with **Django REST Framework** and **Django Channels**. The application provides secure user authentication, private conversations, real-time messaging through WebSockets, online/offline status, last-seen tracking, and password recovery using OTP verification.

## 🚀 Features

### 🔐 Authentication & Security

* User registration and login
* Secure password hashing
* JWT-based authentication
* Protected API endpoints
* Authentication and authorization
* Password reset using OTP verification
* Email-based OTP delivery
* Input validation and error handling
* Protected conversations and messages

### 💬 Real-Time Messaging

* One-to-one conversations
* Real-time messaging using WebSockets
* Send and receive messages instantly
* Message history through REST API
* Message timestamps
* Read/unread message support
* Different message types

### 🟢 User Presence

* Online/offline status
* Last-seen tracking
* WebSocket connection/disconnection handling
* Real-time presence updates

### 👥 Conversations

* Create conversations between users
* Retrieve user's conversations
* Identify the other participant
* Retrieve messages belonging to a conversation
* Secure conversation access

## 🛠️ Technologies Used

### Backend

* **Python**
* **Django**
* **Django REST Framework**
* **Django Channels**
* **WebSockets**
* **JWT Authentication**
* **PostgreSQL**
* **Daphne / ASGI**

### Other Tools

* **Postman** — API testing
* **Git & GitHub** — version control
* **Render** — backend deployment
* **Cloudinary** — profile image storage
* **Gmail brevo** — OTP email delivery

## 📂 Project Structure

```text
chat-app/
│
├── manage.py
│
├── chatty/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── routing.py
│
├── chatt/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── consumers.py
│   ├── routing.py
│   ├── urls.py
│   └── admin.py
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## 🗄️ Main Models

### User

Stores user information such as:

* Username
* Email
* Phone number
* Profile picture
* Online status
* Last seen

### Conversation

Represents a conversation between users.

```text
Conversation
 ├── participants
 └── created_at
```

### Message

Stores individual messages.

```text
Message
 ├── conversation
 ├── sender
 ├── text
 ├── message_type
 ├── is_read
 └── created_at
```

## 🔌 REST API

The application uses REST APIs for authentication, conversations, messages, and user-related operations.

Example endpoints:

```text
POST   /signup/
POST   /login/

POST   /forgot-password/
POST   /verify-otp/
POST   /reset-password/

GET    /conversations/
POST   /conversations/

GET    /messages/?conversation=<id>
POST   /messages/
```

> Endpoint names may vary depending on your final URL configuration.

## ⚡ WebSocket

Real-time chat communication is handled using Django Channels.

WebSocket endpoint:

```text
ws://localhost:8000/ws/chat/<conversation_id>/
```

For example:

```text
ws://localhost:8000/ws/chat/6/
```

When a user connects to a conversation, the WebSocket joins the corresponding chat group.

Messages can then be exchanged without repeatedly refreshing or polling the API.

## 🔄 How Messaging Works

```text
User
  │
  │ REST API
  ▼
Django REST Framework
  │
  ├── Authentication
  ├── Conversation
  └── Message History
       
User
  │
  │ WebSocket
  ▼
Django Channels
  │
  ▼
Chat Consumer
  │
  ▼
Conversation Group
  │
  ├── User A
  └── User B
```

REST APIs are used for operations such as authentication and retrieving stored messages, while **WebSockets handle real-time communication**.

## 🟢 Online Status

The application tracks whether a user is currently connected.

When a WebSocket connection is established:

```text
is_online = True
```

When the connection is closed:

```text
is_online = False
last_seen = current_time
```

This allows the frontend to display information such as:

```text
🟢 Online
```

or:

```text
Last seen 5 minutes ago
```

## 🔑 Password Reset with OTP

The password recovery flow is:

```text
1. User enters phone number
              ↓
2. Server verifies the user
              ↓
3. OTP is generated
              ↓
4. OTP is sent through email
              ↓
5. User submits OTP
              ↓
6. OTP is verified
              ↓
7. User creates a new password
```

OTP verification prevents unauthorized users from changing another user's password.

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <https://github.com/hermelamesfin67-ops/chat-app.git>

```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DATABASE_URL=your-database-url

EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-email-app-password
```

**Never commit ****`.env`**** to GitHub.**

Add it to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

### 8. Run the development server

For ASGI/WebSocket support:

```bash
daphne chatty.asgi:application
```

Or during development:

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## 🧪 API Testing

The APIs can be tested using **Postman**.

Typical testing flow:

```text
1. Register a user
2. Login
3. Obtain authentication token
4. Create a conversation
5. Retrieve conversations
6. Send/retrieve messages
7. Connect to WebSocket
8. Test real-time messaging
9. Test online/offline status
10. Test password reset and OTP verification
```

## 🔒 Security Considerations

The project implements several security practices:

* Passwords are securely hashed by Django.
* Authentication is required for protected endpoints.
* JWT tokens are used for API authentication.
* Conversation access is restricted to participants.
* User input is validated using serializers.
* Sensitive configuration is stored in environment variables.
* `.env` is excluded from version control.
* OTP verification is required during password recovery.

## 🌐 Deployment

The backend can be deployed using an ASGI-compatible hosting platform such as **Render**.

Production configuration should include:

```text
DEBUG=False
```

and properly configured:

```text
ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
DATABASE_URL
SECRET_KEY
EMAIL configuration
```

For production WebSockets, the frontend should connect using:

```text
wss://https://chat-app-2k0b.onrender.com//ws/chat/<conversation_id>/
```

instead of:

```text
ws://localhost:8000/ws/chat/<conversation_id>/
```

## 📌 Future Improvements

Possible future features include:

* Group conversations
* Typing indicators
* Message reactions
* Image/file messages
* Voice messages
* Message deletion
* Message editing
* Push notifications
* Message search
* Blocking users
* Read receipts
* Better WebSocket authentication
* Redis channel layer for scalable WebSocket communication

## 👩‍💻 Author

**Hermela Mesfin**

Backend Developer | Python & Django

This project demonstrates practical experience with:

* REST API development
* Django
* Django REST Framework
* WebSockets
* Django Channels
* Authentication & authorization
* PostgreSQL
* Real-time application architecture
* API security
* Backend deployment

## ⭐ Project Goal

The goal of **Chatty** is to demonstrate how a modern backend can combine **REST APIs and WebSockets** to build a secure, scalable, real-time communication system.

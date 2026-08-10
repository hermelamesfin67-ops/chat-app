from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model


User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):

        query_string = scope.get("query_string", b"").decode()
        print("QUERY:", query_string)

        query_params = parse_qs(query_string)

        token = query_params.get("token", [None])[0]

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]

                scope["user"] = await get_user(user_id)

                print("USER:", scope["user"])
                print(
                    "AUTH:",
                    scope["user"].is_authenticated
                    if scope["user"] else False
                )

            except Exception as e:
                print("JWT ERROR:", repr(e))
                scope["user"] = None
        else:
            scope["user"] = None
            print("NO TOKEN")

        return await self.inner(scope, receive, send)

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        errors = []

        for field, messages in response.data.items():
            if isinstance(messages, list):
                errors.extend(messages)
            else:
                errors.append(messages)

        response.data = {
            "success": False,
            "errors": errors,
        }

    return response


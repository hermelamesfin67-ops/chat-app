import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings


def send_otp_email(to_email, otp):

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    sender = sib_api_v3_sdk.SendSmtpEmailSender(
        email=settings.DEFAULT_FROM_EMAIL,
        name="Chatty"
    )

    recipient = sib_api_v3_sdk.SendSmtpEmailTo(
        email=to_email
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender,
        to=[recipient],
        subject="Chatty Password Reset OTP",
        text_content=f"""
Your Chatty password reset OTP is:

{otp}

This OTP will expire in 5 minutes.

If you did not request a password reset, please ignore this email.

— Chatty Team
"""
    )

    try:
        response = api_instance.send_transac_email(email)
        print("Brevo response:", response)
        return True

    except ApiException as e:
        print("Brevo error:", e)
        return False

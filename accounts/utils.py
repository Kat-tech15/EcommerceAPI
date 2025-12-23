from django.core.mail import send_mail
from .models import EmailOTP
from django.conf import settings
import os

def send_otp_to_user(user):
    otp = EmailOTP.generate_code()
    expires_at = EmailOTP.expiry_time()


    EmailOTP.objects.create(
        user=user,
        code=otp,
        expires_at=expires_at
    )

    send_mail(
        "Your OTP Code ✔",
        f"Your verification code is {otp}",
        os.getenv('EMAIL_HOST_USER'),
        [user.email],
        fail_silently=False,
    )
    
def notify_admin_contact(message_instance):
    subject = f"New contact Message:"
    body = (
        f"Name: {message_instance.name}\n"
        f"Email: {message_instance.email}\n\n"
        f"Message: {message_instance.message}\n\n"
        f"submitted at: {message_instance.created_at}"
    )
    admin_email = settings.EMAIL_HOST_USER
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False
    )
    def send_sms_otp(phone_number, otp_code):
        username = os.getenv('AFRICASTALKING_USERNAME')
        api_key = os.getenv('AFRICASTALKING_API_KEY')

        africastalking.initialize(username, api_key)
        sms = africastalking.SMS 

        message = f"Yuour OTP code is {otp_code}. It expires in 5 minutes."

        response = smsm.send(message, [phone_number])
        return response
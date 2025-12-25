from django.contrib import admin
from .models import EmailOTP, ContactMessage, Profile

admin.site.register(EmailOTP)
admin.site.register(Profile)
admin.site.register(ContactMessage)


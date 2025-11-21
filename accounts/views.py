from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import connection
import random
from .models import EmailOTP, ContactMessage
from datetime  import timedelta
from django.utils import timezone
from rest_framework import permissions, status, generics
from .serializers import UserSerializer, LoginSerializer, ProfileSerializer, EmptySerializer, VerifyOTPSerializer, ResendOTPSerializer, ContactMessageSerializer


class RegisterView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token,_=Token.objects.get_or_create(user=user)
            return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
            email_otp = EmailOTP.objects.get(user=user, code=code)
        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            return Response({'message': 'Invalid OTP or Email'}, status=status.HTTP_400_BAD_REQUEST)

        if email_otp.is_expired():
            return Response({'message': 'OTP has expired, please request for onother OTP to verify your emaail.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_verified == True:
            user.save()
        
        return Response({'message': 'OTP verified successfully!'}, status=status.HTTP_200_OK)

class ResendOTPView(generics.GenericAPIView):
    serializer_class = ResendOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        last_otp = EmailOTP.objects.filter(user=user, is_used=False).order_by('expires_at').first()
        if last_otp:
            if timezone.now() < last_otp.expires_at - timedelta(minutes=5) + timedelta(minutes=5):
                wait_time = (last_otp.expires_at - timezone.now()).seconds
                return Response({'message': f"Please waif {wait_time//60} minutes and {wait_time%60} seconds before requesting for a new OTP."},
                status=status.HTTP_429_TOO_MANY_REQUESTS)
            last_otp.delete()
        
        code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=5)
        otp_instance = EmailOTP.objects.create(code=code, expires_at=expires_at)

        send_otp_to_user(user, otp_instance.code)
        return Response({'message': 'OTP resend successfully, check your email for an OTP to verify your email.'})
            
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(username=username, password=password)

        if user:
            token,created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email
            })
        return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_description="log out logged-in user",
                         responses={200: 'User logged out successfully.'},
                         security=[{'Token': []}])

    def post(self, request):
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()

        return Response({'message': 'User logged out successfully.'}, status=status.HTTP_200_OK)
   
class ProfileDetail(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    
    @swagger_auto_schema(operation_description="Retrieve the logged-in user's profile",
                         responses={200: ProfileSerializer},
                         security=[{'Token': []}])
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_description="Update the logged-in user's profile", 
                         responses={200: ProfileSerializer()},
                         security=[{'Token': []}])
    
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

@api_view(['GET'])
def health_check(request):
    try:
        connection.ensure_connection()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return JsonResponse({
        "status": "OK" if db_status == "connected" else "ERROR",
        "database": db_status,
        "version": "v1.0.0",
        "message": "Ecommerce API is running smoothly."
    })

class ContactMessageCreateView(generics.GenericAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        message_instance = serializer.save()

        notify_admin_contact(message_instance)
    
class ContactMessageAdminView(generics.ListAPIView):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]

class ContactMessageDetailAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]
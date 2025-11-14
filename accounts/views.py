from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.db import connection
from rest_framework import permissions, status, generics
from .serializers import UserSerializer, ProfileSerializer


class RegisterView(generics.GenericAPIView):
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token,_=Token.objects.get_or_create(user=user)
            return Response({'message': 'User registered successfully!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user =authenticate(username=username, password=password)

        if user:
            token,created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email
            })
        return Response({'mesaage': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(generics.GenericAPIView):

    def post(self, request):
        permission_classes = [permissions.IsAuthenticated]

        try:
            request.user.auth_token.delete()
        except:
            pass
        return Response({'message': 'User logged out successfully.'}, status=status.HTTP_201_NO_CONTENT)
   
class ProfileDetail(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_obj(self):
        return self.request.user.profile

def health_check(request):
    try:
        connection.ensure_connection()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return JsonResponse({
        "status": "ok" if db_status == "connected" else "ERROR",
        "database": db_status,
        "version": "v1.0.0",
        "message": "Ecommerce API is running smoothly."
    })



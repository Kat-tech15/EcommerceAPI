from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('profile/', views.ProfileDetail.as_view()),
    path('health/', views.health_check),
]
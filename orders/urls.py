from django.urls import path
from . import views 

urlpatterns = [
    path('list/', views.OrderListView.as_view()),
    path('<int:pk>/', views.OrderDetailView.as_view()),
]
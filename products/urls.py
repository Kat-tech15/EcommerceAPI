from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ProductListView.as_view()),
    path('<int:pk>/',views.ProductDetailView.as_view()),
]
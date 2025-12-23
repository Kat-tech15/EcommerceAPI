from django.urls import path
from . import views

urlpatterns = [
    path('products/<int:product_id>/reviews/', views.ReviewCreateView.as_view()),
]
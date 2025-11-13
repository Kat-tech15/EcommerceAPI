from django.db import models
from products.models import Product

class Order(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField()
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=100, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} - {self.status}"
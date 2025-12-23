from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField(read_only=True)
<<<<<<< HEAD
=======
    rating = serializers.IntegerField(min_value=1, max_value=5)
>>>>>>> f64f5bee031111815c913d53012d6891b85dbca9
    
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'product', 'rating']


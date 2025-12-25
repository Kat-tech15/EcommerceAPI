from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField(read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'product', 'rating']


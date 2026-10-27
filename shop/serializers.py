from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "metal", "stock", "category", "category_name"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Ціна має бути більшою за 0.")
        return value

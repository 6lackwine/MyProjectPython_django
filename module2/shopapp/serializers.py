from shopapp.models import Product, Order
from rest_framework import serializers

class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "price",
            "discount",
            "description",
            "archived",
            "created_at",
            "preview",
        )

class OrderSerializers(serializers.ModelSerializer):
    user = serializers.CharField()
    products = serializers.StringRelatedField(many=True)
    class Meta:
        model = Order
        fields = (
            "pk",
            "user",
            "products",
            "delivery_address",
            "promocode",
            "created_at",
            "receipt",
        )
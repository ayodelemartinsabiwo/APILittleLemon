from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import Group, User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemsSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']


class CartSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(method_name='calculate_price')
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)


    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']

    def calculate_price(self, cart_item:Cart):
        return cart_item.quantity * cart_item.unit_price
        #return product.price * Decimal(1.1)

    def create(self, validated_data):
        menu_item = validated_data['menuitem']

        # Fetch the corresponding menu item
        menu_item_obj = MenuItem.objects.get(pk=menu_item.id)

        # Set the unit price in the Cart object
        validated_data['unit_price'] = menu_item_obj.price

        # Proceed with the regular creation process
        return super().create(validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)  # Use the correct related name. To view the menu items under the order item, remove:source='orderitem_set
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    date = serializers.DateField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']

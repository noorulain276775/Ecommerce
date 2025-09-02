from rest_framework import serializers
from .models import Order, OrderItem, Payment, OrderStatusHistory, Cart, CartItem
from products.serializers import ProductSerializer
from accounts.serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 'unit_price', 
            'total_price', 'product_snapshot'
        ]
        read_only_fields = ['id', 'product_snapshot', 'total_price']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'created_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'created_by']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'payment_status',
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount',
            'total_amount', 'shipping_address', 'billing_address',
            'notes', 'tracking_number', 'items', 'status_history',
            'total_items', 'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'total_amount', 'created_at', 
            'updated_at', 'shipped_at', 'delivered_at'
        ]
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())


class CreateOrderSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = [
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount',
            'shipping_address', 'billing_address', 'notes', 'items'
        ]
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        
        for item in value:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError("Each item must have product_id and quantity.")
            
            if item['quantity'] <= 0:
                raise serializers.ValidationError("Quantity must be greater than 0.")
        
        return value
    
    def validate_shipping_address(self, value):
        required_fields = ['street', 'city', 'state', 'postal_code', 'country']
        for field in required_fields:
            if field not in value or not value[field]:
                raise serializers.ValidationError(f"Shipping address must include {field}.")
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Create order
        order = Order.objects.create(user=user, **validated_data)
        
        # Create order items
        for item_data in items_data:
            from products.models import Product
            product = Product.objects.get(id=item_data['product_id'])
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                unit_price=product.discounted_price or product.price
            )
        
        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            status='PENDING',
            notes='Order created',
            created_by=user
        )
        
        return order


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_method', 'transaction_id', 'amount',
            'status', 'gateway', 'gateway_transaction_id', 'gateway_response',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'order', 'transaction_id', 'gateway_response',
            'created_at', 'updated_at', 'completed_at'
        ]


class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'amount']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_price(self, obj):
        price = obj.product.discounted_price or obj.product.price
        return obj.quantity * price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
    
    def get_total_amount(self, obj):
        total = 0
        for item in obj.items.all():
            price = item.product.discounted_price or item.product.price
            total += item.quantity * price
        return total


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_product_id(self, value):
        from products.models import Product
        try:
            Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive.")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

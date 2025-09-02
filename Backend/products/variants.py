from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
import uuid

class ProductVariant(models.Model):
    """Product variants for different sizes, colors, etc."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit")
    name = models.CharField(max_length=200, help_text="Variant name (e.g., 'Red - Large')")
    
    # Variant attributes
    size = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Weight in grams")
    
    # Pricing
    price_modifier = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Additional cost for this variant (can be negative for discounts)"
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    
    # Additional fields
    barcode = models.CharField(max_length=50, blank=True, null=True)
    dimensions = models.JSONField(default=dict, blank=True, help_text="Length, width, height")
    images = models.JSONField(default=list, blank=True, help_text="Additional variant images")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'size', 'color']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['stock_quantity']),
        ]
    
    def __str__(self):
        return f"{self.product.title} - {self.name}"
    
    @property
    def final_price(self):
        """Calculate final price including variant modifier"""
        return self.product.price + self.price_modifier
    
    @property
    def is_low_stock(self):
        """Check if variant is low on stock"""
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def is_out_of_stock(self):
        """Check if variant is out of stock"""
        return self.stock_quantity == 0
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_sku()
        if not self.name:
            self.name = self.generate_name()
        super().save(*args, **kwargs)
    
    def generate_sku(self):
        """Generate unique SKU for variant"""
        base_sku = self.product.slug[:8].upper()
        variant_id = str(self.id)[:8].upper()
        return f"{base_sku}-{variant_id}"
    
    def generate_name(self):
        """Generate variant name from attributes"""
        attributes = []
        if self.color:
            attributes.append(self.color)
        if self.size:
            attributes.append(self.size)
        if self.material:
            attributes.append(self.material)
        
        return " - ".join(attributes) if attributes else "Default"

class VariantAttribute(models.Model):
    """Define possible attributes for product variants"""
    ATTRIBUTE_TYPES = [
        ('size', 'Size'),
        ('color', 'Color'),
        ('material', 'Material'),
        ('weight', 'Weight'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    attribute_type = models.CharField(max_length=20, choices=ATTRIBUTE_TYPES)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # For predefined values (like sizes: S, M, L, XL)
    predefined_values = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['attribute_type', 'is_active']),
        ]
    
    def __str__(self):
        return self.display_name

class VariantImage(models.Model):
    """Additional images for product variants"""
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='variant_images')
    image = models.ImageField(upload_to='variant_images/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', 'created_at']
        indexes = [
            models.Index(fields=['variant', 'is_primary']),
        ]
    
    def __str__(self):
        return f"{self.variant.name} - Image {self.sort_order}"

class VariantPricing(models.Model):
    """Dynamic pricing for variants based on conditions"""
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='pricing_rules')
    
    # Pricing conditions
    min_quantity = models.PositiveIntegerField(default=1)
    max_quantity = models.PositiveIntegerField(blank=True, null=True)
    
    # Customer type pricing
    customer_type = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All Customers'),
            ('wholesale', 'Wholesale'),
            ('retail', 'Retail'),
            ('vip', 'VIP'),
        ],
        default='all'
    )
    
    # Pricing
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    percentage_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['variant', 'is_active', 'valid_from']),
            models.Index(fields=['customer_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.variant.name} - {self.customer_type} pricing"
    
    def is_valid(self):
        """Check if pricing rule is currently valid"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.valid_from > now:
            return False
        
        if self.valid_until and self.valid_until < now:
            return False
        
        return True
    
    def calculate_price(self, base_price, quantity=1):
        """Calculate final price based on this pricing rule"""
        if not self.is_valid():
            return base_price
        
        if not (self.min_quantity <= quantity <= (self.max_quantity or float('inf'))):
            return base_price
        
        # Apply percentage discount first
        if self.percentage_discount > 0:
            discount_amount = base_price * (self.percentage_discount / 100)
            base_price = base_price - discount_amount
        
        # Apply price modifier
        final_price = base_price + self.price_modifier
        
        return max(0, final_price)  # Ensure price is not negative

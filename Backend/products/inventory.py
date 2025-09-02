from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class InventoryTransaction(models.Model):
    """Track all inventory movements"""
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Adjustment'),
        ('TRANSFER', 'Transfer'),
        ('RETURN', 'Return'),
        ('DAMAGE', 'Damage'),
        ('LOSS', 'Loss'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='inventory_transactions')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, null=True, blank=True, related_name='inventory_transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Reference information
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    reference_type = models.CharField(max_length=50, blank=True, null=True)  # 'order', 'purchase', 'adjustment', etc.
    notes = models.TextField(blank=True)
    
    # User who performed the transaction
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Stock levels before and after
    stock_before = models.PositiveIntegerField()
    stock_after = models.PositiveIntegerField()
    
    # Cost information
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['product', 'transaction_date']),
            models.Index(fields=['variant', 'transaction_date']),
            models.Index(fields=['transaction_type', 'transaction_date']),
            models.Index(fields=['reference_type', 'reference_number']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.title} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Calculate total cost if unit cost is provided
        if self.unit_cost and not self.total_cost:
            self.total_cost = self.unit_cost * abs(self.quantity)
        
        super().save(*args, **kwargs)

class StockAlert(models.Model):
    """Stock level alerts and notifications"""
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('OVERSTOCK', 'Overstock'),
        ('EXPIRING', 'Expiring Soon'),
        ('EXPIRED', 'Expired'),
    ]
    
    ALERT_LEVELS = [
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_alerts')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, null=True, blank=True, related_name='stock_alerts')
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVELS)
    
    current_stock = models.PositiveIntegerField()
    threshold_value = models.PositiveIntegerField()
    message = models.TextField()
    
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_resolved']),
            models.Index(fields=['alert_type', 'alert_level']),
            models.Index(fields=['is_resolved', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.title}"
    
    def resolve(self, user=None):
        """Mark alert as resolved"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        if user:
            self.resolved_by = user
        self.save()

class InventoryLocation(models.Model):
    """Physical locations where inventory is stored"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    # Location details
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'is_primary']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class StockLocation(models.Model):
    """Stock levels at specific locations"""
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_locations')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, null=True, blank=True, related_name='stock_locations')
    location = models.ForeignKey(InventoryLocation, on_delete=models.CASCADE, related_name='stock_items')
    
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)
    
    # Reorder levels
    reorder_point = models.PositiveIntegerField(default=0)
    reorder_quantity = models.PositiveIntegerField(default=0)
    
    # Last updated
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'variant', 'location']
        indexes = [
            models.Index(fields=['product', 'location']),
            models.Index(fields=['variant', 'location']),
            models.Index(fields=['available_quantity']),
        ]
    
    def __str__(self):
        variant_name = f" - {self.variant.name}" if self.variant else ""
        return f"{self.product.title}{variant_name} at {self.location.name}"
    
    def save(self, *args, **kwargs):
        # Calculate available quantity
        self.available_quantity = max(0, self.quantity - self.reserved_quantity)
        super().save(*args, **kwargs)
    
    @property
    def needs_reorder(self):
        """Check if this item needs to be reordered"""
        return self.available_quantity <= self.reorder_point

class InventoryReport(models.Model):
    """Generated inventory reports"""
    REPORT_TYPES = [
        ('STOCK_LEVEL', 'Stock Level Report'),
        ('MOVEMENT', 'Movement Report'),
        ('VALUATION', 'Valuation Report'),
        ('ALERTS', 'Alerts Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Report parameters
    parameters = models.JSONField(default=dict, blank=True)
    
    # Generated by
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Report data
    data = models.JSONField(default=dict, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    
    # Status
    status = models.CharField(max_length=20, default='PENDING', choices=[
        ('PENDING', 'Pending'),
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['generated_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class InventorySettings(models.Model):
    """Global inventory settings"""
    # Stock alerts
    low_stock_threshold = models.PositiveIntegerField(default=10)
    out_of_stock_alert = models.BooleanField(default=True)
    low_stock_alert = models.BooleanField(default=True)
    
    # Auto-reorder
    auto_reorder_enabled = models.BooleanField(default=False)
    default_reorder_quantity = models.PositiveIntegerField(default=100)
    
    # Inventory valuation
    valuation_method = models.CharField(max_length=20, default='FIFO', choices=[
        ('FIFO', 'First In, First Out'),
        ('LIFO', 'Last In, First Out'),
        ('AVERAGE', 'Average Cost'),
    ])
    
    # Negative stock
    allow_negative_stock = models.BooleanField(default=False)
    
    # Audit settings
    require_transaction_approval = models.BooleanField(default=False)
    audit_trail_retention_days = models.PositiveIntegerField(default=365)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inventory Settings"
        verbose_name_plural = "Inventory Settings"
    
    def __str__(self):
        return "Inventory Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and InventorySettings.objects.exists():
            raise ValueError("Only one InventorySettings instance is allowed")
        super().save(*args, **kwargs)

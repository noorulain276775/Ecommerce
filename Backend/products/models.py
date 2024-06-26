from django.db import models

class Seller(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(max_length=1000)
    shop_logo = models.ImageField(upload_to='logo')

class Category(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='category')

class Product(models.Model):
    title = models.CharField(max_length=256, unique=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    product_number = models.CharField(max_length=12, unique=True)
    is_active = models.BooleanField(default=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.discount_percentage > 0:
            self.discounted_price = self.price - (self.price * self.discount_percentage / 100)
        else:
            self.discounted_price = None
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')
    created_at = models.DateTimeField(auto_now_add=True)

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Seller(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(max_length=1000)
    shop_logo = models.ImageField(upload_to='logo')

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='category')

    def __str__(self):
        return self.name

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
    slug = models.SlugField(max_length=256, unique=True, blank=True, default='default-slug')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.discount_percentage > 0:
            self.discounted_price = self.price - (self.price * self.discount_percentage / 100)
        else:
            self.discounted_price = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

@receiver(pre_save, sender=Product)
def pre_save_product_receiver(sender, instance, *args, **kwargs):
    if not instance.slug or instance.slug == 'default-slug':
        instance.slug = slugify(instance.title)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')
    created_at = models.DateTimeField(auto_now_add=True)

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

from django.db import models
from django.utils.text import slugify
from accounts.models import CustomUser

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
    title = models.CharField(max_length=25, unique=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    product_number = models.CharField(max_length=12, unique=True)
    is_active = models.BooleanField(default=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    featured_image = models.ImageField(upload_to='product_images', default='users/person.png')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, blank=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    flash_sale = models.BooleanField(default=False)
    best_seller_product = models.BooleanField(default=False)
    featured_product = models.BooleanField(default=False)
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

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')
    created_at = models.DateTimeField(auto_now_add=True)

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

class Review(models.Model):
    ONE_TO_FIVE_RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )

    product_rating = models.IntegerField(choices=ONE_TO_FIVE_RATING_CHOICES)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.product.title}'

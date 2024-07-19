from django.contrib import admin
from .models import Seller, Review, Product, Category

# Register your models here.
admin.site.register(Seller)
admin.site.register(Review)
admin.site.register(Product)
admin.site.register(Category)
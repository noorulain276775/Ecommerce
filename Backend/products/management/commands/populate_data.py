from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import Seller, Category, Product, Inventory
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate database with sample data...')
        
        # Create Sellers
        sellers_data = [
            {
                'name': 'TechStore Pro',
                'description': 'Your one-stop shop for the latest technology and gadgets. We offer premium electronics with competitive prices and excellent customer service.',
            },
            {
                'name': 'Fashion Hub',
                'description': 'Trendy fashion for men and women. From casual wear to formal attire, we have everything you need to look your best.',
            },
            {
                'name': 'Home & Living',
                'description': 'Transform your home with our beautiful collection of furniture, decor, and home essentials.',
            },
            {
                'name': 'Sports Central',
                'description': 'Everything you need for your fitness journey. From gym equipment to outdoor gear, we have it all.',
            },
            {
                'name': 'Beauty Essentials',
                'description': 'Premium beauty and skincare products from top brands. Look and feel your best every day.',
            }
        ]
        
        sellers = []
        for seller_data in sellers_data:
            seller, created = Seller.objects.get_or_create(
                name=seller_data['name'],
                defaults=seller_data
            )
            sellers.append(seller)
            if created:
                self.stdout.write(f'Created seller: {seller.name}')
        
        # Create Categories
        categories_data = [
            {
                'name': 'Electronics',
            },
            {
                'name': 'Fashion',
            },
            {
                'name': 'Home & Garden',
            },
            {
                'name': 'Sports & Fitness',
            },
            {
                'name': 'Beauty & Health',
            },
            {
                'name': 'Books & Media',
            }
        ]
        
        categories = []
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create Products
        products_data = [
            # Electronics
            {
                'title': 'iPhone 15 Pro Max',
                'description': 'The most advanced iPhone with titanium design, A17 Pro chip, and Pro camera system.',
                'product_number': 'IPH15PM001',
                'seller': sellers[0],  # TechStore Pro
                'category': categories[0],  # Electronics
                'price': 1199.99,
                'discount_percentage': 10.0,
                'flash_sale': True,
                'best_seller_product': True,
                'featured_product': True,
            },
            {
                'title': 'Samsung Galaxy S24 Ultra',
                'description': 'Premium Android smartphone with S Pen, 200MP camera, and all-day battery life.',
                'product_number': 'SGS24U001',
                'seller': sellers[0],  # TechStore Pro
                'category': categories[0],  # Electronics
                'price': 1299.99,
                'discount_percentage': 15.0,
                'flash_sale': True,
                'best_seller_product': False,
                'featured_product': True,
            },
            {
                'title': 'MacBook Pro 16-inch',
                'description': 'Powerful laptop with M3 Pro chip, Liquid Retina XDR display, and all-day battery.',
                'product_number': 'MBP16M3001',
                'seller': sellers[0],  # TechStore Pro
                'category': categories[0],  # Electronics
                'price': 2499.99,
                'discount_percentage': 5.0,
                'flash_sale': False,
                'best_seller_product': True,
                'featured_product': True,
            },
            {
                'title': 'Sony WH-1000XM5 Headphones',
                'description': 'Industry-leading noise canceling wireless headphones with 30-hour battery life.',
                'product_number': 'SONYWH001',
                'seller': sellers[0],  # TechStore Pro
                'category': categories[0],  # Electronics
                'price': 399.99,
                'discount_percentage': 20.0,
                'flash_sale': True,
                'best_seller_product': False,
                'featured_product': False,
            },
            {
                'title': 'iPad Air 5th Gen',
                'description': 'Powerful tablet with M1 chip, 10.9-inch Liquid Retina display, and Apple Pencil support.',
                'product_number': 'IPADAIR001',
                'seller': sellers[0],  # TechStore Pro
                'category': categories[0],  # Electronics
                'price': 599.99,
                'discount_percentage': 12.0,
                'flash_sale': False,
                'best_seller_product': True,
                'featured_product': False,
            },
            
            # Fashion
            {
                'title': 'Designer Leather Jacket',
                'description': 'Premium genuine leather jacket with modern design and perfect fit.',
                'product_number': 'LEATH001',
                'seller': sellers[1],  # Fashion Hub
                'category': categories[1],  # Fashion
                'price': 299.99,
                'discount_percentage': 25.0,
                'flash_sale': True,
                'best_seller_product': False,
                'featured_product': True,
            },
            {
                'title': 'Casual Denim Jeans',
                'description': 'Comfortable and stylish denim jeans perfect for everyday wear.',
                'product_number': 'DENIM001',
                'seller': sellers[1],  # Fashion Hub
                'category': categories[1],  # Fashion
                'price': 89.99,
                'discount_percentage': 30.0,
                'flash_sale': True,
                'best_seller_product': True,
                'featured_product': False,
            },
            {
                'title': 'Elegant Evening Dress',
                'description': 'Beautiful evening dress perfect for special occasions and formal events.',
                'product_number': 'DRESS001',
                'seller': sellers[1],  # Fashion Hub
                'category': categories[1],  # Fashion
                'price': 199.99,
                'discount_percentage': 15.0,
                'flash_sale': False,
                'best_seller_product': False,
                'featured_product': True,
            },
            
            # Home & Garden
            {
                'title': 'Smart Home Speaker',
                'description': 'Voice-controlled smart speaker with premium sound quality and smart home integration.',
                'product_number': 'SMART001',
                'seller': sellers[2],  # Home & Living
                'category': categories[2],  # Home & Garden
                'price': 149.99,
                'discount_percentage': 20.0,
                'flash_sale': True,
                'best_seller_product': True,
                'featured_product': False,
            },
            {
                'title': 'Modern Coffee Table',
                'description': 'Sleek and modern coffee table perfect for any living room.',
                'product_number': 'TABLE001',
                'seller': sellers[2],  # Home & Living
                'category': categories[2],  # Home & Garden
                'price': 399.99,
                'discount_percentage': 10.0,
                'flash_sale': False,
                'best_seller_product': False,
                'featured_product': True,
            },
            
            # Sports & Fitness
            {
                'title': 'Premium Yoga Mat',
                'description': 'High-quality yoga mat with excellent grip and cushioning for all yoga practices.',
                'product_number': 'YOGA001',
                'seller': sellers[3],  # Sports Central
                'category': categories[3],  # Sports & Fitness
                'price': 79.99,
                'discount_percentage': 25.0,
                'flash_sale': True,
                'best_seller_product': True,
                'featured_product': False,
            },
            {
                'title': 'Adjustable Dumbbells Set',
                'description': 'Space-saving adjustable dumbbells perfect for home workouts.',
                'product_number': 'DUMB001',
                'seller': sellers[3],  # Sports Central
                'category': categories[3],  # Sports & Fitness
                'price': 299.99,
                'discount_percentage': 15.0,
                'flash_sale': False,
                'best_seller_product': False,
                'featured_product': True,
            },
            
            # Beauty & Health
            {
                'title': 'Anti-Aging Serum',
                'description': 'Premium anti-aging serum with vitamin C and hyaluronic acid for youthful skin.',
                'product_number': 'SERUM001',
                'seller': sellers[4],  # Beauty Essentials
                'category': categories[4],  # Beauty & Health
                'price': 89.99,
                'discount_percentage': 30.0,
                'flash_sale': True,
                'best_seller_product': True,
                'featured_product': True,
            },
            {
                'title': 'Organic Face Moisturizer',
                'description': 'Natural and organic face moisturizer for all skin types.',
                'product_number': 'MOIST001',
                'seller': sellers[4],  # Beauty Essentials
                'category': categories[4],  # Beauty & Health
                'price': 49.99,
                'discount_percentage': 20.0,
                'flash_sale': True,
                'best_seller_product': False,
                'featured_product': False,
            },
            
            # Books & Media
            {
                'title': 'Programming Fundamentals',
                'description': 'Comprehensive guide to programming fundamentals for beginners.',
                'product_number': 'BOOK001',
                'seller': sellers[0],  # TechStore Pro
                'category': categories[5],  # Books & Media
                'price': 39.99,
                'discount_percentage': 10.0,
                'flash_sale': False,
                'best_seller_product': True,
                'featured_product': False,
            },
            {
                'title': 'Digital Marketing Guide',
                'description': 'Complete guide to digital marketing strategies and techniques.',
                'product_number': 'BOOK002',
                'seller': sellers[0],  # TechStore Pro
                'category': categories[5],  # Books & Media
                'price': 29.99,
                'discount_percentage': 15.0,
                'flash_sale': True,
                'best_seller_product': False,
                'featured_product': True,
            }
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                product_number=product_data['product_number'],
                defaults=product_data
            )
            if created:
                self.stdout.write(f'Created product: {product.title}')
                
                # Create inventory for the product
                Inventory.objects.create(
                    product=product,
                    stock=50  # Default stock of 50
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
        self.stdout.write(f'Created {len(sellers)} sellers')
        self.stdout.write(f'Created {len(categories)} categories')
        self.stdout.write(f'Created {len(products_data)} products')

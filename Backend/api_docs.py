"""
Comprehensive API Documentation Configuration
"""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import status

# API Documentation Decorators and Schemas

# Authentication API Documentation
auth_schemas = {
    'register': extend_schema(
        summary="User Registration",
        description="Register a new user account with phone number and password",
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'Registration Request',
                summary='User Registration',
                description='Example of user registration request',
                value={
                    "phone": "1234567890",
                    "password": "securepassword123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "date_of_birth": "1990-01-01"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Registration Response',
                summary='Registration Success',
                description='Successful registration response',
                value={
                    "message": "User registered successfully",
                    "user": {
                        "id": 1,
                        "phone": "1234567890",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@example.com",
                        "date_of_birth": "1990-01-01",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00Z"
                    },
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                },
                response_only=True,
            )
        ]
    ),
    
    'login': extend_schema(
        summary="User Login",
        description="Authenticate user with phone number and password",
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'Login Request',
                summary='User Login',
                description='Example of user login request',
                value={
                    "phone": "1234567890",
                    "password": "securepassword123"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Login Response',
                summary='Login Success',
                description='Successful login response',
                value={
                    "message": "Login successful",
                    "user": {
                        "id": 1,
                        "phone": "1234567890",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@example.com"
                    },
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                },
                response_only=True,
            )
        ]
    ),
    
    'refresh_token': extend_schema(
        summary="Refresh Access Token",
        description="Get new access token using refresh token",
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'Token Refresh Request',
                summary='Refresh Token',
                description='Example of token refresh request',
                value={
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                },
                request_only=True,
            ),
            OpenApiExample(
                'Token Refresh Response',
                summary='Token Refresh Success',
                description='Successful token refresh response',
                value={
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                },
                response_only=True,
            )
        ]
    ),
    
    'logout': extend_schema(
        summary="User Logout",
        description="Logout user and blacklist tokens",
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'Logout Request',
                summary='User Logout',
                description='Example of user logout request',
                value={
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                },
                request_only=True,
            ),
            OpenApiExample(
                'Logout Response',
                summary='Logout Success',
                description='Successful logout response',
                value={
                    "message": "Logout successful"
                },
                response_only=True,
            )
        ]
    ),
    
    'forgot_password': extend_schema(
        summary="Forgot Password",
        description="Send OTP to user's phone for password reset",
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'Forgot Password Request',
                summary='Forgot Password',
                description='Example of forgot password request',
                value={
                    "phone": "1234567890"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Forgot Password Response',
                summary='OTP Sent',
                description='OTP sent successfully response',
                value={
                    "message": "OTP sent successfully",
                    "phone": "1234567890"
                },
                response_only=True,
            )
        ]
    ),
    
    'verify_otp': extend_schema(
        summary="Verify OTP",
        description="Verify OTP for password reset",
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'OTP Verification Request',
                summary='Verify OTP',
                description='Example of OTP verification request',
                value={
                    "phone": "1234567890",
                    "otp": "123456"
                },
                request_only=True,
            ),
            OpenApiExample(
                'OTP Verification Response',
                summary='OTP Verified',
                description='OTP verified successfully response',
                value={
                    "message": "OTP verified successfully",
                    "verified": True
                },
                response_only=True,
            )
        ]
    ),
    
    'reset_password': extend_schema(
        summary="Reset Password",
        description="Reset user password after OTP verification",
        tags=['Authentication'],
        examples=[
            OpenApiExample(
                'Reset Password Request',
                summary='Reset Password',
                description='Example of password reset request',
                value={
                    "phone": "1234567890",
                    "new_password": "newsecurepassword123"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Reset Password Response',
                summary='Password Reset',
                description='Password reset successfully response',
                value={
                    "message": "Password reset successfully"
                },
                response_only=True,
            )
        ]
    )
}

# Product API Documentation
product_schemas = {
    'list_products': extend_schema(
        summary="List Products",
        description="Get paginated list of products with filtering and search",
        tags=['Products'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search products by title or description'
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by category ID'
            ),
            OpenApiParameter(
                name='min_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Minimum price filter'
            ),
            OpenApiParameter(
                name='max_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Maximum price filter'
            ),
            OpenApiParameter(
                name='featured_product',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter featured products'
            ),
            OpenApiParameter(
                name='best_seller_product',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter best seller products'
            ),
            OpenApiParameter(
                name='flash_sale',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter flash sale products'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Ordering field (e.g., price, -created_at)'
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of items per page'
            )
        ],
        examples=[
            OpenApiExample(
                'Products List Response',
                summary='Products List',
                description='Example of products list response',
                value={
                    "count": 100,
                    "next": "http://api.example.com/products/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "title": "Premium Wireless Headphones",
                            "description": "High-quality wireless headphones with noise cancellation",
                            "price": "199.99",
                            "discount_price": "149.99",
                            "category": {
                                "id": 1,
                                "name": "Electronics",
                                "slug": "electronics"
                            },
                            "seller": {
                                "id": 1,
                                "name": "TechStore",
                                "email": "contact@techstore.com"
                            },
                            "images": [
                                "http://api.example.com/media/product_images/headphones1.jpg"
                            ],
                            "featured_product": True,
                            "best_seller_product": False,
                            "flash_sale": False,
                            "is_active": True,
                            "created_at": "2024-01-01T00:00:00Z"
                        }
                    ]
                },
                response_only=True,
            )
        ]
    ),
    
    'create_product': extend_schema(
        summary="Create Product",
        description="Create a new product (Seller only)",
        tags=['Products'],
        examples=[
            OpenApiExample(
                'Create Product Request',
                summary='Create Product',
                description='Example of product creation request',
                value={
                    "title": "Premium Wireless Headphones",
                    "description": "High-quality wireless headphones with noise cancellation",
                    "price": "199.99",
                    "discount_price": "149.99",
                    "category": 1,
                    "images": [
                        "http://api.example.com/media/product_images/headphones1.jpg"
                    ],
                    "featured_product": True,
                    "best_seller_product": False,
                    "flash_sale": False
                },
                request_only=True,
            )
        ]
    ),
    
    'get_product': extend_schema(
        summary="Get Product Details",
        description="Get detailed information about a specific product",
        tags=['Products'],
        examples=[
            OpenApiExample(
                'Product Detail Response',
                summary='Product Details',
                description='Example of product detail response',
                value={
                    "id": 1,
                    "title": "Premium Wireless Headphones",
                    "description": "High-quality wireless headphones with noise cancellation",
                    "price": "199.99",
                    "discount_price": "149.99",
                    "category": {
                        "id": 1,
                        "name": "Electronics",
                        "slug": "electronics",
                        "description": "Electronic devices and accessories"
                    },
                    "seller": {
                        "id": 1,
                        "name": "TechStore",
                        "email": "contact@techstore.com",
                        "phone": "1234567890"
                    },
                    "images": [
                        "http://api.example.com/media/product_images/headphones1.jpg",
                        "http://api.example.com/media/product_images/headphones2.jpg"
                    ],
                    "variants": [
                        {
                            "id": "uuid-here",
                            "name": "Black - Large",
                            "sku": "HEAD-BL-L",
                            "size": "Large",
                            "color": "Black",
                            "price_modifier": "0.00",
                            "stock_quantity": 50,
                            "is_active": True
                        }
                    ],
                    "reviews": [
                        {
                            "id": 1,
                            "user": {
                                "id": 2,
                                "first_name": "Jane",
                                "last_name": "Smith"
                            },
                            "rating": 5,
                            "comment": "Excellent sound quality!",
                            "created_at": "2024-01-15T10:30:00Z"
                        }
                    ],
                    "featured_product": True,
                    "best_seller_product": False,
                    "flash_sale": False,
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                },
                response_only=True,
            )
        ]
    )
}

# Order API Documentation
order_schemas = {
    'list_orders': extend_schema(
        summary="List User Orders",
        description="Get paginated list of user's orders",
        tags=['Orders'],
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by order status'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Ordering field (e.g., -created_at, total_amount)'
            )
        ]
    ),
    
    'create_order': extend_schema(
        summary="Create Order",
        description="Create a new order from cart items",
        tags=['Orders'],
        examples=[
            OpenApiExample(
                'Create Order Request',
                summary='Create Order',
                description='Example of order creation request',
                value={
                    "shipping_address": {
                        "street": "123 Main St",
                        "city": "New York",
                        "state": "NY",
                        "zip_code": "10001",
                        "country": "USA"
                    },
                    "payment_method": "credit_card",
                    "notes": "Please deliver during business hours"
                },
                request_only=True,
            )
        ]
    ),
    
    'get_order': extend_schema(
        summary="Get Order Details",
        description="Get detailed information about a specific order",
        tags=['Orders']
    )
}

# Search API Documentation
search_schemas = {
    'advanced_search': extend_schema(
        summary="Advanced Product Search",
        description="Advanced search with multiple filters and sorting options",
        tags=['Search'],
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query'
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Category ID filter'
            ),
            OpenApiParameter(
                name='min_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Minimum price'
            ),
            OpenApiParameter(
                name='max_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Maximum price'
            ),
            OpenApiParameter(
                name='seller',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Seller ID filter'
            ),
            OpenApiParameter(
                name='rating',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Minimum rating filter'
            ),
            OpenApiParameter(
                name='sort_by',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Sort field (price, rating, created_at)'
            ),
            OpenApiParameter(
                name='sort_order',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Sort order (asc, desc)'
            )
        ]
    )
}

# Analytics API Documentation
analytics_schemas = {
    'sales_analytics': extend_schema(
        summary="Sales Analytics",
        description="Get sales analytics and reports",
        tags=['Analytics'],
        parameters=[
            OpenApiParameter(
                name='period',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Time period (daily, weekly, monthly, yearly)'
            ),
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date for analytics'
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date for analytics'
            )
        ]
    )
}

# Error Response Schemas
error_schemas = {
    '400_error': extend_schema(
        summary="Bad Request",
        description="Request validation error",
        examples=[
            OpenApiExample(
                'Validation Error',
                summary='Validation Error Response',
                description='Example of validation error response',
                value={
                    "error": "Validation failed",
                    "details": {
                        "phone": ["This field is required."],
                        "password": ["This field must be at least 8 characters long."]
                    }
                },
                response_only=True,
            )
        ]
    ),
    
    '401_error': extend_schema(
        summary="Unauthorized",
        description="Authentication required or invalid credentials",
        examples=[
            OpenApiExample(
                'Unauthorized Error',
                summary='Unauthorized Response',
                description='Example of unauthorized response',
                value={
                    "error": "Authentication credentials were not provided."
                },
                response_only=True,
            )
        ]
    ),
    
    '403_error': extend_schema(
        summary="Forbidden",
        description="Insufficient permissions",
        examples=[
            OpenApiExample(
                'Forbidden Error',
                summary='Forbidden Response',
                description='Example of forbidden response',
                value={
                    "error": "You do not have permission to perform this action."
                },
                response_only=True,
            )
        ]
    ),
    
    '404_error': extend_schema(
        summary="Not Found",
        description="Resource not found",
        examples=[
            OpenApiExample(
                'Not Found Error',
                summary='Not Found Response',
                description='Example of not found response',
                value={
                    "error": "Product not found."
                },
                response_only=True,
            )
        ]
    ),
    
    '500_error': extend_schema(
        summary="Internal Server Error",
        description="Server error",
        examples=[
            OpenApiExample(
                'Server Error',
                summary='Server Error Response',
                description='Example of server error response',
                value={
                    "error": "An unexpected error occurred. Please try again later."
                },
                response_only=True,
            )
        ]
    )
}

# API View Decorators
def api_view_docs(schema_func):
    """Decorator to apply API documentation to views"""
    def decorator(view_class):
        return extend_schema_view(**schema_func())(view_class)
    return decorator

# Rate Limiting Documentation
rate_limit_info = {
    'authentication': {
        'register': '5 requests per minute per IP',
        'login': '10 requests per minute per IP',
        'forgot_password': '3 requests per minute per IP',
        'verify_otp': '10 requests per minute per IP',
        'resend_otp': '2 requests per minute per IP',
        'reset_password': '5 requests per minute per IP',
        'refresh_token': '20 requests per minute per IP'
    },
    'general': {
        'product_list': '100 requests per hour per IP',
        'product_detail': '200 requests per hour per IP',
        'search': '50 requests per hour per IP',
        'order_operations': '30 requests per hour per user'
    }
}

# API Versioning Information
api_versions = {
    'v1': {
        'version': '1.0.0',
        'release_date': '2024-01-01',
        'status': 'stable',
        'deprecation_date': None,
        'changelog': [
            'Initial API release',
            'Authentication system',
            'Product management',
            'Order processing',
            'Search functionality'
        ]
    }
}

# API Usage Examples
usage_examples = {
    'authentication_flow': {
        'description': 'Complete authentication flow example',
        'steps': [
            '1. Register new user account',
            '2. Login with credentials',
            '3. Use access token for authenticated requests',
            '4. Refresh token when access token expires',
            '5. Logout to invalidate tokens'
        ],
        'code_examples': {
            'javascript': '''
// Register new user
const registerResponse = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        phone: '1234567890',
        password: 'securepassword123',
        first_name: 'John',
        last_name: 'Doe'
    })
});

// Login
const loginResponse = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        phone: '1234567890',
        password: 'securepassword123'
    })
});

const { access_token } = await loginResponse.json();

// Use token for authenticated requests
const productsResponse = await fetch('/api/products/', {
    headers: { 'Authorization': `Bearer ${access_token}` }
});
            ''',
            'python': '''
import requests

# Register new user
register_data = {
    'phone': '1234567890',
    'password': 'securepassword123',
    'first_name': 'John',
    'last_name': 'Doe'
}
register_response = requests.post('/api/auth/register/', json=register_data)

# Login
login_data = {
    'phone': '1234567890',
    'password': 'securepassword123'
}
login_response = requests.post('/api/auth/login/', json=login_data)
access_token = login_response.json()['access_token']

# Use token for authenticated requests
headers = {'Authorization': f'Bearer {access_token}'}
products_response = requests.get('/api/products/', headers=headers)
            '''
        }
    }
}

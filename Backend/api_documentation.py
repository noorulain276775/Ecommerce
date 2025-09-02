"""
Comprehensive API Documentation for E-commerce Backend

This module provides detailed documentation for all API endpoints,
including request/response examples, authentication requirements,
and error handling.
"""

API_DOCUMENTATION = {
    "title": "E-commerce API",
    "version": "1.0.0",
    "description": "A comprehensive e-commerce API built with Django REST Framework",
    "base_url": "http://127.0.0.1:8000",
    
    "authentication": {
        "type": "JWT Token",
        "header": "Authorization: Bearer <token>",
        "description": "Include JWT token in Authorization header for protected endpoints"
    },
    
    "endpoints": {
        "authentication": {
            "register": {
                "url": "/accounts/register/",
                "method": "POST",
                "description": "Register a new user",
                "authentication": "None",
                "request_body": {
                    "phone": "string (required)",
                    "password": "string (required, min 8 chars)",
                    "first_name": "string (required)",
                    "last_name": "string (required)",
                    "date_of_birth": "date (required, YYYY-MM-DD)",
                    "user_type": "string (choices: CUSTOMER, SELLER)"
                },
                "response": {
                    "201": {
                        "description": "User created successfully",
                        "body": {
                            "id": "integer",
                            "phone": "string",
                            "first_name": "string",
                            "last_name": "string",
                            "date_of_birth": "date",
                            "user_type": "string"
                        }
                    },
                    "400": {
                        "description": "Validation error",
                        "body": {
                            "error": "string or object"
                        }
                    }
                }
            },
            
            "login": {
                "url": "/accounts/login/",
                "method": "POST",
                "description": "Authenticate user and get JWT token",
                "authentication": "None",
                "request_body": {
                    "phone": "string (required)",
                    "password": "string (required)"
                },
                "response": {
                    "200": {
                        "description": "Login successful",
                        "body": {
                            "message": "Login Successful",
                            "token": "string (JWT)",
                            "user": {
                                "phone": "string",
                                "id": "integer"
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid credentials",
                        "body": {
                            "message": "Either phone number or password is wrong!"
                        }
                    }
                }
            },
            
            "forgot_password": {
                "url": "/accounts/forgot-password/",
                "method": "POST",
                "description": "Request password reset OTP",
                "authentication": "None",
                "request_body": {
                    "phone": "string (required)"
                },
                "response": {
                    "200": {
                        "description": "OTP sent successfully",
                        "body": {
                            "message": "OTP sent successfully",
                            "otp": "string (6 digits)"
                        }
                    },
                    "404": {
                        "description": "User not found",
                        "body": {
                            "message": "User with this phone number does not exist"
                        }
                    }
                }
            },
            
            "verify_otp": {
                "url": "/accounts/verify-otp/",
                "method": "POST",
                "description": "Verify OTP for password reset",
                "authentication": "None",
                "request_body": {
                    "phone": "string (required)",
                    "otp": "string (required, 6 digits)"
                },
                "response": {
                    "200": {
                        "description": "OTP verified successfully",
                        "body": {
                            "message": "OTP verified successfully"
                        }
                    },
                    "400": {
                        "description": "Invalid or expired OTP",
                        "body": {
                            "message": "Invalid OTP or OTP has expired"
                        }
                    }
                }
            },
            
            "reset_password": {
                "url": "/accounts/reset-password/",
                "method": "POST",
                "description": "Reset password after OTP verification",
                "authentication": "None",
                "request_body": {
                    "phone": "string (required)",
                    "password": "string (required, min 8 chars)"
                },
                "response": {
                    "200": {
                        "description": "Password reset successfully",
                        "body": {
                            "message": "Password reset successfully"
                        }
                    },
                    "400": {
                        "description": "Phone not verified or validation error",
                        "body": {
                            "message": "Phone number not verified or validation error"
                        }
                    }
                }
            }
        },
        
        "products": {
            "list_products": {
                "url": "/api/products/",
                "method": "GET",
                "description": "Get list of products with filtering and pagination",
                "authentication": "None",
                "query_parameters": {
                    "flash_sale": "boolean (optional)",
                    "best_seller_product": "boolean (optional)",
                    "featured_product": "boolean (optional)",
                    "page": "integer (optional, default: 1)",
                    "page_size": "integer (optional, default: 20)"
                },
                "response": {
                    "200": {
                        "description": "Products retrieved successfully",
                        "body": {
                            "count": "integer",
                            "next": "string (URL or null)",
                            "previous": "string (URL or null)",
                            "results": [
                                {
                                    "id": "integer",
                                    "title": "string",
                                    "description": "string",
                                    "price": "decimal",
                                    "discount_percentage": "decimal",
                                    "discounted_price": "decimal",
                                    "featured_image": "string (URL)",
                                    "category": "object",
                                    "seller": "object",
                                    "average_rating": "decimal",
                                    "user_count": "integer",
                                    "flash_sale": "boolean",
                                    "best_seller_product": "boolean",
                                    "featured_product": "boolean"
                                }
                            ]
                        }
                    }
                }
            },
            
            "product_detail": {
                "url": "/api/products/{id}/",
                "method": "GET",
                "description": "Get detailed information about a specific product",
                "authentication": "None",
                "response": {
                    "200": {
                        "description": "Product details retrieved successfully",
                        "body": {
                            "id": "integer",
                            "title": "string",
                            "description": "string",
                            "price": "decimal",
                            "discount_percentage": "decimal",
                            "discounted_price": "decimal",
                            "featured_image": "string (URL)",
                            "category": "object",
                            "seller": "object",
                            "average_rating": "decimal",
                            "user_count": "integer",
                            "flash_sale": "boolean",
                            "best_seller_product": "boolean",
                            "featured_product": "boolean"
                        }
                    },
                    "404": {
                        "description": "Product not found",
                        "body": {
                            "error": "Product not found"
                        }
                    }
                }
            },
            
            "create_product": {
                "url": "/api/products/",
                "method": "POST",
                "description": "Create a new product (authenticated users only)",
                "authentication": "Required",
                "request_body": {
                    "title": "string (required, max 25 chars)",
                    "description": "string (optional, max 1000 chars)",
                    "category": "integer (required, category ID)",
                    "seller": "integer (required, seller ID)",
                    "price": "decimal (required)",
                    "discount_percentage": "decimal (optional)",
                    "featured_image": "file (optional)",
                    "flash_sale": "boolean (optional)",
                    "best_seller_product": "boolean (optional)",
                    "featured_product": "boolean (optional)"
                },
                "response": {
                    "201": {
                        "description": "Product created successfully",
                        "body": "Product object"
                    },
                    "400": {
                        "description": "Validation error",
                        "body": {
                            "error": "string or object"
                        }
                    },
                    "401": {
                        "description": "Authentication required",
                        "body": {
                            "error": "Authentication required"
                        }
                    }
                }
            }
        },
        
        "categories": {
            "list_categories": {
                "url": "/api/categories/",
                "method": "GET",
                "description": "Get list of all categories",
                "authentication": "None",
                "response": {
                    "200": {
                        "description": "Categories retrieved successfully",
                        "body": [
                            {
                                "id": "integer",
                                "name": "string",
                                "image": "string (URL)"
                            }
                        ]
                    }
                }
            }
        },
        
        "sellers": {
            "list_sellers": {
                "url": "/api/sellers/",
                "method": "GET",
                "description": "Get list of all sellers",
                "authentication": "None",
                "response": {
                    "200": {
                        "description": "Sellers retrieved successfully",
                        "body": [
                            {
                                "id": "integer",
                                "name": "string",
                                "description": "string",
                                "shop_logo": "string (URL)"
                            }
                        ]
                    }
                }
            }
        },
        
        "cart": {
            "get_cart": {
                "url": "/api/orders/cart/",
                "method": "GET",
                "description": "Get user's shopping cart",
                "authentication": "Required",
                "response": {
                    "200": {
                        "description": "Cart retrieved successfully",
                        "body": {
                            "id": "integer",
                            "items": [
                                {
                                    "id": "integer",
                                    "product": "object",
                                    "quantity": "integer",
                                    "total_price": "decimal"
                                }
                            ],
                            "total_items": "integer",
                            "total_amount": "decimal"
                        }
                    }
                }
            },
            
            "add_to_cart": {
                "url": "/api/orders/cart/",
                "method": "POST",
                "description": "Add item to cart",
                "authentication": "Required",
                "request_body": {
                    "product_id": "integer (required)",
                    "quantity": "integer (required, min: 1)"
                },
                "response": {
                    "201": {
                        "description": "Item added to cart successfully",
                        "body": "Cart item object"
                    },
                    "400": {
                        "description": "Validation error or insufficient stock",
                        "body": {
                            "error": "string"
                        }
                    }
                }
            },
            
            "update_cart_item": {
                "url": "/api/orders/cart/items/{item_id}/",
                "method": "PUT",
                "description": "Update cart item quantity",
                "authentication": "Required",
                "request_body": {
                    "quantity": "integer (required, min: 1)"
                },
                "response": {
                    "200": {
                        "description": "Cart item updated successfully",
                        "body": "Cart item object"
                    },
                    "400": {
                        "description": "Validation error or insufficient stock",
                        "body": {
                            "error": "string"
                        }
                    }
                }
            },
            
            "remove_cart_item": {
                "url": "/api/orders/cart/items/{item_id}/",
                "method": "DELETE",
                "description": "Remove item from cart",
                "authentication": "Required",
                "response": {
                    "204": {
                        "description": "Item removed successfully"
                    }
                }
            }
        },
        
        "orders": {
            "create_order": {
                "url": "/api/orders/orders/",
                "method": "POST",
                "description": "Create order from cart",
                "authentication": "Required",
                "request_body": {
                    "shipping_address": {
                        "street": "string (required)",
                        "city": "string (required)",
                        "state": "string (required)",
                        "postal_code": "string (required)",
                        "country": "string (required)"
                    },
                    "billing_address": "object (optional, same structure as shipping_address)",
                    "notes": "string (optional)"
                },
                "response": {
                    "201": {
                        "description": "Order created successfully",
                        "body": "Order object with items and totals"
                    },
                    "400": {
                        "description": "Validation error or insufficient stock",
                        "body": {
                            "error": "string"
                        }
                    }
                }
            },
            
            "list_orders": {
                "url": "/api/orders/orders/",
                "method": "GET",
                "description": "Get user's orders",
                "authentication": "Required",
                "response": {
                    "200": {
                        "description": "Orders retrieved successfully",
                        "body": [
                            {
                                "id": "uuid",
                                "order_number": "string",
                                "status": "string",
                                "payment_status": "string",
                                "total_amount": "decimal",
                                "items": "array",
                                "created_at": "datetime"
                            }
                        ]
                    }
                }
            },
            
            "order_detail": {
                "url": "/api/orders/orders/{id}/",
                "method": "GET",
                "description": "Get detailed order information",
                "authentication": "Required",
                "response": {
                    "200": {
                        "description": "Order details retrieved successfully",
                        "body": "Complete order object with items and status history"
                    }
                }
            },
            
            "create_payment": {
                "url": "/api/orders/orders/{order_id}/payment/",
                "method": "POST",
                "description": "Create payment for order",
                "authentication": "Required",
                "request_body": {
                    "payment_method": "string (required, choices: CARD, PAYPAL, BANK_TRANSFER, COD)",
                    "amount": "decimal (required)"
                },
                "response": {
                    "201": {
                        "description": "Payment created successfully",
                        "body": "Payment object"
                    }
                }
            }
        },
        
        "search": {
            "advanced_search": {
                "url": "/api/search/",
                "method": "GET",
                "description": "Advanced product search with filters and sorting",
                "authentication": "None",
                "query_parameters": {
                    "q": "string (optional, search query)",
                    "category": "string (optional)",
                    "min_price": "decimal (optional)",
                    "max_price": "decimal (optional)",
                    "seller": "string (optional)",
                    "sort_by": "string (optional, choices: relevance, price_low, price_high, newest, oldest, rating, popularity, discount)",
                    "page": "integer (optional, default: 1)",
                    "page_size": "integer (optional, default: 20)"
                },
                "response": {
                    "200": {
                        "description": "Search results with pagination",
                        "body": {
                            "results": "array of products",
                            "pagination": {
                                "current_page": "integer",
                                "total_pages": "integer",
                                "total_count": "integer",
                                "has_next": "boolean",
                                "has_previous": "boolean"
                            },
                            "filters_applied": "object"
                        }
                    }
                }
            },
            
            "search_suggestions": {
                "url": "/api/search/suggestions/",
                "method": "GET",
                "description": "Get search suggestions",
                "authentication": "None",
                "query_parameters": {
                    "q": "string (required, min 2 chars)"
                },
                "response": {
                    "200": {
                        "description": "Search suggestions",
                        "body": {
                            "suggestions": "array of strings"
                        }
                    }
                }
            },
            
            "filter_options": {
                "url": "/api/search/filters/",
                "method": "GET",
                "description": "Get available filter options",
                "authentication": "None",
                "response": {
                    "200": {
                        "description": "Filter options",
                        "body": {
                            "categories": "array",
                            "price_range": "object",
                            "sellers": "array",
                            "sort_options": "array"
                        }
                    }
                }
            }
        }
    },
    
    "error_responses": {
        "400": {
            "description": "Bad Request - Validation error or invalid data",
            "body": {
                "error": "string or object with field-specific errors"
            }
        },
        "401": {
            "description": "Unauthorized - Authentication required",
            "body": {
                "error": "Authentication required"
            }
        },
        "403": {
            "description": "Forbidden - Insufficient permissions",
            "body": {
                "error": "Permission denied"
            }
        },
        "404": {
            "description": "Not Found - Resource not found",
            "body": {
                "error": "Resource not found"
            }
        },
        "500": {
            "description": "Internal Server Error - Server error",
            "body": {
                "error": "Internal server error"
            }
        }
    },
    
    "rate_limiting": {
        "description": "API endpoints are rate limited to prevent abuse",
        "limits": {
            "authentication": "5 requests per minute per IP",
            "general": "100 requests per hour per user",
            "search": "50 requests per minute per IP"
        }
    },
    
    "examples": {
        "register_user": {
            "request": {
                "phone": "1234567890",
                "password": "securepassword123",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
                "user_type": "CUSTOMER"
            },
            "response": {
                "id": 1,
                "phone": "1234567890",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
                "user_type": "CUSTOMER"
            }
        },
        
        "create_order": {
            "request": {
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "postal_code": "10001",
                    "country": "USA"
                },
                "notes": "Please deliver after 5 PM"
            },
            "response": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "order_number": "ORD-20240101120000-550E8400",
                "status": "PENDING",
                "payment_status": "PENDING",
                "total_amount": "129.99",
                "items": [
                    {
                        "product": "iPhone 15 Pro Max",
                        "quantity": 1,
                        "unit_price": "1199.99"
                    }
                ]
            }
        }
    }
}

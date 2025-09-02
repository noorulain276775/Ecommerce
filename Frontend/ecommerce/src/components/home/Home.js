// Home.js
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchFlashSaleProducts } from "../../store/slices/flashSaleSlice";
import { fetchFeaturedProducts } from "../../store/slices/featuredProductsSlice";
import { fetchBestSellers } from "../../store/slices/bestSellersSlice";
import { fetchAllProducts } from "../../store/slices/allProductsSlice";
import { fetchCategories } from "../../store/slices/categoriesSlice";
import Navbar from "../Navbar/Navbar";
import SeoBar from "../SEOBar/SeoBar";
import FlashSale from "../FlashSale/FlashSale";
import ProductSection from "../ProductSection/ProductSection";
import ProductGrid from "../ProductGrid/ProductGrid";
import CategoryFilter from "../CategoryFilter/CategoryFilter";
import { FaFilter, FaShoppingBag, FaStar, FaTruck, FaShieldAlt, FaHeadset } from "react-icons/fa";
import "./Home.css";

export default function Home() {
  const dispatch = useDispatch();
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({});
  
  const flashSale = useSelector((state) => state.flashSale);
  const featuredProducts = useSelector((state) => state.featuredProducts);
  const bestSellers = useSelector((state) => state.bestSellers);
  const allProducts = useSelector((state) => state.allProducts);
  const categories = useSelector((state) => state.categories);

  useEffect(() => {
    dispatch(fetchFlashSaleProducts());
    dispatch(fetchFeaturedProducts());
    dispatch(fetchBestSellers());
    dispatch(fetchAllProducts());
    dispatch(fetchCategories());
  }, [dispatch]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    dispatch(fetchAllProducts(newFilters));
  };

  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };

  return (
    <div className="home-container">
      <Navbar />
      <SeoBar />
      
      {/* Hero Banner */}
      <section className="hero-banner">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              Discover Amazing Products
              <span className="gradient-text"> at Unbeatable Prices</span>
            </h1>
            <p className="hero-description">
              Shop from thousands of products across multiple categories. 
              Fast delivery, secure payments, and exceptional customer service.
            </p>
            <div className="hero-buttons">
              <button className="cta-button primary">
                <FaShoppingBag />
                Shop Now
              </button>
              <button className="cta-button secondary">
                View Categories
              </button>
            </div>
          </div>
          <div className="hero-image">
            <div className="floating-card">
              <div className="card-content">
                <FaStar className="card-icon" />
                <div className="card-text">
                  <span className="card-number">50K+</span>
                  <span className="card-label">Happy Customers</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-container">
          <div className="feature-item">
            <div className="feature-icon">
              <FaTruck />
            </div>
            <h3>Free Shipping</h3>
            <p>Free delivery on orders over $50</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <FaShieldAlt />
            </div>
            <h3>Secure Payment</h3>
            <p>100% secure and encrypted payments</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <FaHeadset />
            </div>
            <h3>24/7 Support</h3>
            <p>Round-the-clock customer support</p>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="categories-section">
        <div className="section-header">
          <h2 className="section-title">Shop by Category</h2>
          <p className="section-subtitle">Explore our wide range of product categories</p>
        </div>
        <div className="categories-grid">
          {categories.data?.slice(0, 6).map((category) => (
            <div key={category.id} className="category-card">
              <div className="category-image">
                <img src={category.image || '/api/placeholder/200/200'} alt={category.name} />
              </div>
              <div className="category-info">
                <h3>{category.name}</h3>
                <p>Shop Now</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Flash Sale Section */}
      <section className="flash-sale-section">
        <FlashSale 
          data={flashSale.data} 
          isLoading={flashSale.isLoading} 
          isError={flashSale.isError} 
        />
      </section>
      
      {/* Featured Products Section */}
      <section className="featured-section">
        <ProductSection
          title="Featured Products"
          data={featuredProducts.data}
          isLoading={featuredProducts.isLoading}
          isError={featuredProducts.isError}
        />
      </section>
      
      {/* Best Sellers Section */}
      <section className="bestsellers-section">
        <ProductSection
          title="Best Sellers"
          data={bestSellers.data}
          isLoading={bestSellers.isLoading}
          isError={bestSellers.isError}
        />
      </section>

      {/* All Products Section */}
      <section className="all-products-section">
        <div className="section-header">
          <h1 className="section-title">All Products</h1>
          <button className="filter-toggle-btn" onClick={toggleFilters}>
            <FaFilter />
            <span>Filters</span>
          </button>
        </div>
        
        <ProductGrid
          title=""
          products={allProducts.data}
          isLoading={allProducts.isLoading}
          isError={allProducts.isError}
        />
      </section>

      {/* Newsletter Section */}
      <section className="newsletter-section">
        <div className="newsletter-container">
          <div className="newsletter-content">
            <h2>Stay Updated</h2>
            <p>Subscribe to our newsletter and get 10% off your first order</p>
            <div className="newsletter-form">
              <input type="email" placeholder="Enter your email address" />
              <button>Subscribe</button>
            </div>
          </div>
        </div>
      </section>

      {/* Category Filter Sidebar */}
      <CategoryFilter
        isOpen={showFilters}
        onClose={() => setShowFilters(false)}
        onFilterChange={handleFilterChange}
      />

      {/* Overlay for mobile */}
      {showFilters && (
        <div className="filter-overlay" onClick={() => setShowFilters(false)} />
      )}
    </div>
  );
}

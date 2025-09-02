import React from "react";
import ProductCard from "../ProductCard/ProductCard";
import "./ProductGrid.css";

const ProductGrid = ({ products, isLoading, isError, title }) => {
  if (isLoading) {
    return (
      <div className="product-grid-container">
        <div className="grid-header">
          <h2 className="grid-title">{title}</h2>
        </div>
        <div className="loading-grid">
          {[...Array(8)].map((_, index) => (
            <div key={index} className="product-skeleton">
              <div className="skeleton-image"></div>
              <div className="skeleton-content">
                <div className="skeleton-title"></div>
                <div className="skeleton-price"></div>
                <div className="skeleton-rating"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="product-grid-container">
        <div className="grid-header">
          <h2 className="grid-title">{title}</h2>
        </div>
        <div className="error-message">
          <div className="error-icon">⚠️</div>
          <h3>Oops! Something went wrong</h3>
          <p>We couldn't load the products. Please try again later.</p>
        </div>
      </div>
    );
  }

  const productList = products?.results || products || [];

  if (productList.length === 0) {
    return (
      <div className="product-grid-container">
        <div className="grid-header">
          <h2 className="grid-title">{title}</h2>
        </div>
        <div className="empty-message">
          <div className="empty-icon">📦</div>
          <h3>No products found</h3>
          <p>Try adjusting your filters or search terms.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="product-grid-container">
      <div className="grid-header">
        <h2 className="grid-title">{title}</h2>
        <div className="product-count">
          {productList.length} {productList.length === 1 ? 'product' : 'products'}
        </div>
      </div>
      
      <div className="product-grid">
        {productList.map((product) => (
          <div key={product.id} className="grid-item">
            <ProductCard
              title={product.title}
              image={product.featured_image}
              current_price={product.discounted_price}
              original_price={product.price}
              percentage={product.discount_percentage}
              rating={product.average_rating || 0}
              user_count={product.user_count || 0}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductGrid;

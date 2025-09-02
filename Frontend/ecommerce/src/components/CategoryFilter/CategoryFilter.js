import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchAllProducts } from "../../store/slices/allProductsSlice";
import { fetchCategories } from "../../store/slices/categoriesSlice";
import "./CategoryFilter.css";
import { FaFilter, FaTimes, FaChevronDown, FaChevronUp } from "react-icons/fa";

const CategoryFilter = ({ isOpen, onClose, onFilterChange }) => {
  const dispatch = useDispatch();
  const { data: categories, isLoading } = useSelector((state) => state.categories);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [showPriceFilter, setShowPriceFilter] = useState(false);

  React.useEffect(() => {
    dispatch(fetchCategories());
  }, [dispatch]);

  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId);
    onFilterChange({ category: categoryId });
  };

  const handlePriceFilter = () => {
    const filters = {};
    if (priceRange.min) filters.minPrice = priceRange.min;
    if (priceRange.max) filters.maxPrice = priceRange.max;
    if (selectedCategory) filters.category = selectedCategory;
    
    onFilterChange(filters);
  };

  const clearFilters = () => {
    setSelectedCategory(null);
    setPriceRange({ min: '', max: '' });
    onFilterChange({});
  };

  return (
    <div className={`category-filter ${isOpen ? 'open' : ''}`}>
      <div className="filter-header">
        <div className="filter-title">
          <FaFilter />
          <span>Filters</span>
        </div>
        <button className="close-btn" onClick={onClose}>
          <FaTimes />
        </button>
      </div>

      <div className="filter-content">
        {/* Categories */}
        <div className="filter-section">
          <div className="section-header">
            <h3>Categories</h3>
          </div>
          <div className="category-list">
            <button
              className={`category-item ${!selectedCategory ? 'active' : ''}`}
              onClick={() => handleCategorySelect(null)}
            >
              All Categories
            </button>
            {isLoading ? (
              <div className="loading">Loading categories...</div>
            ) : (
              categories?.map((category) => (
                <button
                  key={category.id}
                  className={`category-item ${selectedCategory === category.id ? 'active' : ''}`}
                  onClick={() => handleCategorySelect(category.id)}
                >
                  {category.name}
                </button>
              ))
            )}
          </div>
        </div>

        {/* Price Range */}
        <div className="filter-section">
          <div className="section-header">
            <h3>Price Range</h3>
            <button
              className="toggle-btn"
              onClick={() => setShowPriceFilter(!showPriceFilter)}
            >
              {showPriceFilter ? <FaChevronUp /> : <FaChevronDown />}
            </button>
          </div>
          {showPriceFilter && (
            <div className="price-filter">
              <div className="price-inputs">
                <input
                  type="number"
                  placeholder="Min Price"
                  value={priceRange.min}
                  onChange={(e) => setPriceRange({ ...priceRange, min: e.target.value })}
                />
                <span>-</span>
                <input
                  type="number"
                  placeholder="Max Price"
                  value={priceRange.max}
                  onChange={(e) => setPriceRange({ ...priceRange, max: e.target.value })}
                />
              </div>
              <button className="apply-price-btn" onClick={handlePriceFilter}>
                Apply
              </button>
            </div>
          )}
        </div>

        {/* Clear Filters */}
        <div className="filter-actions">
          <button className="clear-filters-btn" onClick={clearFilters}>
            Clear All Filters
          </button>
        </div>
      </div>
    </div>
  );
};

export default CategoryFilter;

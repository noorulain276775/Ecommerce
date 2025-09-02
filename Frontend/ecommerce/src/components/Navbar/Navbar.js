import React, { useState } from "react";
import "./navbar.css";
import Lotus from "../../assets/images/logo.svg";
import { FaSearch, FaBars, FaTimes } from "react-icons/fa";
import { MdOutlineShoppingCartCheckout } from "react-icons/md";
import { FaRegHeart, FaUser } from "react-icons/fa";
import { GrCurrency } from "react-icons/gr";
import { useSelector } from "react-redux";
import { isAuthenticated, logout } from "../../utils/auth";

const Navbar = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showCurrencyDropdown, setShowCurrencyDropdown] = useState(false);
  const [selectedCurrency, setSelectedCurrency] = useState("USD");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user } = useSelector((state) => state.login);

  const handleSearch = () => {
    // Make backend call with searchTerm
    console.log(`Searching for ${searchTerm}`);
  };

  const toggleCurrencyDropdown = () => {
    setShowCurrencyDropdown(!showCurrencyDropdown);
  };

  const handleCurrencySelect = (currency) => {
    setSelectedCurrency(currency);
    setShowCurrencyDropdown(false);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <nav className="modern-nav">
      <div className="nav-container">
        {/* Logo */}
        <div className="nav-logo">
          <img src={Lotus} alt="logo" className="logo-image" />
          <span className="brand-name">ShopHub</span>
        </div>

        {/* Search Bar */}
        <div className="search-container">
          <div className="search-bar">
            <input
              type="text"
              className="search-input"
              placeholder="Search for products, brands and more..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button className="search-btn" onClick={handleSearch}>
              <FaSearch />
            </button>
          </div>
        </div>

        {/* Desktop Navigation */}
        <div className="nav-actions">
          <div className="nav-item">
            <button className="nav-icon-btn">
              <FaRegHeart />
              <span className="nav-label">Wishlist</span>
            </button>
          </div>
          
          <div className="nav-item">
            <button className="nav-icon-btn">
              <MdOutlineShoppingCartCheckout />
              <span className="nav-label">Cart</span>
              <span className="cart-badge">0</span>
            </button>
          </div>

          <div className="nav-item currency-dropdown" onClick={toggleCurrencyDropdown}>
            <button className="nav-icon-btn">
              <GrCurrency />
              <span className="nav-label">{selectedCurrency}</span>
            </button>
            {showCurrencyDropdown && (
              <div className="dropdown-menu">
                <div className="dropdown-item" onClick={() => handleCurrencySelect("USD")}>USD</div>
                <div className="dropdown-item" onClick={() => handleCurrencySelect("EUR")}>EUR</div>
                <div className="dropdown-item" onClick={() => handleCurrencySelect("GBP")}>GBP</div>
              </div>
            )}
          </div>

          <div className="nav-item">
            {isAuthenticated() && user ? (
              <div className="user-menu">
                <button className="nav-icon-btn">
                  <FaUser />
                  <span className="nav-label">{user.phone}</span>
                </button>
                <button className="logout-btn" onClick={logout}>
                  Logout
                </button>
              </div>
            ) : (
              <a href="/login" className="login-btn">
                <FaUser />
                Sign In
              </a>
            )}
          </div>
        </div>

        {/* Mobile Menu Button */}
        <button className="mobile-menu-btn" onClick={toggleMobileMenu}>
          {isMobileMenuOpen ? <FaTimes /> : <FaBars />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="mobile-menu">
          <div className="mobile-search">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <button onClick={handleSearch}>
              <FaSearch />
            </button>
          </div>
          <div className="mobile-nav-items">
            <a href="/wishlist" className="mobile-nav-item">
              <FaRegHeart />
              Wishlist
            </a>
            <a href="/cart" className="mobile-nav-item">
              <MdOutlineShoppingCartCheckout />
              Cart
            </a>
            {isAuthenticated() && user ? (
              <div className="mobile-user-section">
                <div className="mobile-user-info">
                  <FaUser />
                  {user.phone}
                </div>
                <button className="mobile-logout-btn" onClick={logout}>
                  Logout
                </button>
              </div>
            ) : (
              <a href="/login" className="mobile-nav-item">
                <FaUser />
                Sign In
              </a>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;

import React, { useState } from "react";
import "./navbar.css";
import Lotus from "../../assets/images/logo.svg";
import { FaSearch } from "react-icons/fa";
import { MdOutlineShoppingCartCheckout } from "react-icons/md";
import { FaRegHeart } from "react-icons/fa";
// import { GrLanguage } from "react-icons/gr";
import { GrCurrency } from "react-icons/gr";

const Navbar = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
  const [showCurrencyDropdown, setShowCurrencyDropdown] = useState(false);
  // const [selectedLanguage, setSelectedLanguage] = useState("English");
  const [selectedCurrency, setSelectedCurrency] = useState("USD");

  const handleSearch = () => {
    // Make backend call with searchTerm
    console.log(`Searching for ${searchTerm}`);
  };

  const toggleLanguageDropdown = () => {
    setShowLanguageDropdown(!showLanguageDropdown);
    setShowCurrencyDropdown(false);
  };

  const toggleCurrencyDropdown = () => {
    setShowCurrencyDropdown(!showCurrencyDropdown);
    setShowLanguageDropdown(false);
  };

  // const handleLanguageSelect = (language) => {
  //   setSelectedLanguage(language);
  //   setShowLanguageDropdown(false);
  // };

  const handleCurrencySelect = (currency) => {
    setSelectedCurrency(currency);
    setShowCurrencyDropdown(false);
  };

  return (
    <nav className="nav">
      <img src={Lotus} alt="logo" className="logo-image" />
      <div className="searchBar">
        <input
          type="text"
          className="searchInput"
          placeholder="Search your product"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <FaSearch className="searchIcon" onClick={handleSearch} />
      </div>
      <div className="navMenu">
        <li className="navItem">
          <a href="/dummy" className="navLink">
            <MdOutlineShoppingCartCheckout size={25} color="#007bff" />
          </a>
        </li>
        <li className="navItem">
          <a href="/dummy" className="navLink">
            <FaRegHeart size={25} color="#007bff" />
          </a>
        </li>
        {/* <li className="navItem" onClick={toggleLanguageDropdown}>
          <span className="navLink">
            <GrLanguage size={25} color="#007bff" />
            {selectedLanguage}
          </span>
          {showLanguageDropdown && (
            <ul className="dropdownMenu">
              <li onClick={() => handleLanguageSelect("English")}>English</li>
              <li onClick={() => handleLanguageSelect("Spanish")}>Spanish</li>
              <li onClick={() => handleLanguageSelect("French")}>French</li>
            </ul>
          )}
        </li> */}
        <li className="navItem" onClick={toggleCurrencyDropdown}>
          <span className="navLink">
            <GrCurrency size={30} color="#007bff" />
            {selectedCurrency}
          </span>
          {showCurrencyDropdown && (
            <ul className="dropdownMenu">
              <li onClick={() => handleCurrencySelect("USD")}>USD</li>
              <li onClick={() => handleCurrencySelect("EUR")}>EUR</li>
              <li onClick={() => handleCurrencySelect("GBP")}>GBP</li>
            </ul>
          )}
        </li>
      </div>
      <nav className="navBtn">
        <a href="/login" className="navBtnLink">
          Sign In
        </a>
      </nav>
    </nav>
  );
};

export default Navbar;

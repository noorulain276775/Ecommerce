import React, { useState } from 'react';
import './navbar.css';
import Lotus from "../../assets/images/logo.svg";
import { FaSearch } from 'react-icons/fa';

const Navbar = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = () => {
    // Make backend call with searchTerm
    console.log(`Searching for ${searchTerm}`);
  };

  return (
    <nav className="nav">
      <img src={Lotus} alt="logo" className='logo-image' />
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
            Cart
          </a>
        </li>
        <li className="navItem">
          <a href="/dummy" className="navLink">
            Currency
          </a>
        </li>
        <li className="navItem">
          <a href="/dummy" className="navLink">
            Language
          </a>
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

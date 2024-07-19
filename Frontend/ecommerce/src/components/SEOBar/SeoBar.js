import React from "react";
import "./SeoBar.css";
import { IoIosArrowForward } from "react-icons/io";

const SeoBar = (props) => {
  return (
    <div className="mainSeo">
      <div className="linksMain">
        <div className="internalLinks">
          <div className="linkArrow">
            <a href="/dummy">Woman's Fashion</a>
            <IoIosArrowForward />
          </div>
          <div className="linkArrow">
            <a href="/dummy">Man's Fashion</a>
            <IoIosArrowForward />
          </div>
          <a href="/dummy">Electronics</a>
          <a href="/dummy">Home & Lifestyle</a>
          <a href="/dummy">Medicine</a>
          <a href="/dummy">Sports & Outdoor</a>
          <a href="/dummy">Baby & Toys</a>
          <a href="/dummy">Groceries & Pets</a>
          <a href="/dummy">Health & Beauty</a>
        </div>
      </div>
    </div>
  );
};

export default SeoBar;

import React, { useState } from "react";
import "./productCard.css";
import Rating from "@mui/material/Rating";
import ShoppingCartOutlinedIcon from "@mui/icons-material/ShoppingCartOutlined";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import API_URL from "../../constant";

const ProductCard = ({
  title,
  current_price,
  original_price,
  percentage,
  rating,
  image,
  user_count,
}) => {
  const [isFavorite, setIsFavorite] = useState(false);

  const handleFavoriteClick = () => {
    setIsFavorite(!isFavorite);
  };

  console.log("Discounted price", current_price);
  console.log("Original price", original_price);

  return (
    <div className="productCard">
      {percentage > 0.0 && <div className="discountTag">-{percentage}%</div>}

      <div className="favoriteIcon" onClick={handleFavoriteClick}>
        {isFavorite ? <ShoppingCartIcon /> : <ShoppingCartOutlinedIcon />}
      </div>
      <img src={`${API_URL}` + image} alt={title} className="productImage" />
      <p className="productName">{title}</p>
      <div className="productPrice">
        {current_price ? (
          <>
            <span className="currentPrice">{current_price} AED</span>
            <span className="originalPrice">{original_price} AED</span>
          </>
        ) : (
          <span className="currentPrice">{original_price} AED</span>
        )}
      </div>
      <Rating name="read-only" value={rating} readOnly />
      <span className="reviewsCount">({user_count})</span>
    </div>
  );
};

export default ProductCard;

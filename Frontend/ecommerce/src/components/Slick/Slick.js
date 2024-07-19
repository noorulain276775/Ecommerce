import "slick-carousel/slick/slick.css"; 
import "slick-carousel/slick/slick-theme.css";
import React from 'react';
import Slider from 'react-slick';
import "./Slider.css"; // Add your custom styles here

const SimpleSlider = () => {
  const settings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
  };

  return (
    <Slider {...settings}>
      <div className="slide">
        <img src="path_to_your_image1" alt="Slide 1" className="slide-image" />
        <div className="slide-content">
          <h2>iPhone 14 Series</h2>
          <p>Up to 10% off Voucher</p>
          <a href="/shop" className="shop-now">Shop Now</a>
        </div>
      </div>
      <div className="slide">
        <img src="path_to_your_image2" alt="Slide 2" className="slide-image" />
        <div className="slide-content">
          <h2>Another Product</h2>
          <p>Special Discount</p>
          <a href="/shop" className="shop-now">Shop Now</a>
        </div>
      </div>
      {/* Add more slides as needed */}
    </Slider>
  );
};

export default SimpleSlider;



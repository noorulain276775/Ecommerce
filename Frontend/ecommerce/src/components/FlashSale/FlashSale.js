import React, { useRef } from "react";
import Slider from "react-slick";
import "./flash.css";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import { FaCircleArrowRight } from "react-icons/fa6";
import { FaCircleArrowLeft } from "react-icons/fa6";
import ProductCard from "../ProductCard/ProductCard";

const FlashSale = ({ data, isLoading, isError }) => {
  const sliderRef = useRef(null);

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error loading flash sale products</div>;

  const SampleNextArrow = (props) => {
    const { onClick } = props;
    return (
      <div
        className="custom-next-arrow"
        onClick={onClick}
      >
        <FaCircleArrowRight style={{ fontSize: "40px" }} />
      </div>
    );
  };

  const SamplePrevArrow = (props) => {
    const { onClick } = props;
    return (
      <div
        className="custom-prev-arrow"
        onClick={onClick}
      >
        <FaCircleArrowLeft style={{ fontSize: "40px" }} />
      </div>
    );
  };

  const settings = {
    dots: false,
    infinite: true,
    speed: 500,
    slidesToShow: 4,
    slidesToScroll: 1,
    responsive: [
      {
        breakpoint: 1140,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 1,
          infinite: true,
        },
      },
      {
        breakpoint: 840,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
    ],
  };

  return (
    <div className="flashContainer">
      <div className="flashHeader">
        <h1 className="flashHeading">Flash Sale</h1>
        <div className="flashArrows">
          <div onClick={() => sliderRef.current.slickPrev()}>
            <SamplePrevArrow />
          </div>
          <div onClick={() => sliderRef.current.slickNext()}>
            <SampleNextArrow />
          </div>
        </div>
      </div>

      <Slider {...settings} ref={sliderRef} className="flashProducts">
        {data &&
          data.map((product) => (
            <div key={product.id}>
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
      </Slider>
    </div>
  );
};

export default FlashSale;

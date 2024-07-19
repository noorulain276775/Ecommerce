// Home.js
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchFlashSaleProducts } from "../../store/slices/flashSaleSlice";
import Navbar from "../Navbar/Navbar";
import SeoBar from "../SEOBar/SeoBar";
import FlashSale from "../FlashSale/FlashSale";

export default function Home() {
  const dispatch = useDispatch();
  const flashSale = useSelector((state) => state.flashSale);
  console.log(flashSale)

  useEffect(() => {
    dispatch(fetchFlashSaleProducts());
  }, [dispatch]);

  return (
    <>
      <Navbar />
      <SeoBar />
      <FlashSale data={flashSale.data} isLoading={flashSale.isLoading} isError={flashSale.isError} />
    </>
  );
}

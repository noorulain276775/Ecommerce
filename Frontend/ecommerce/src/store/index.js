// store/index.js
import { configureStore } from '@reduxjs/toolkit';
import sellerReducer from './slices/sellerSlice';
import loginReducer from './slices/loginSlice';
import registerReducer from './slices/registerSlice'
import flashSaleReducer from './slices/flashSaleSlice'
import featuredProductsReducer from './slices/featuredProductsSlice'
import bestSellersReducer from './slices/bestSellersSlice'
import categoriesReducer from './slices/categoriesSlice'
import allProductsReducer from './slices/allProductsSlice'

const store = configureStore({
    reducer: {
        seller: sellerReducer,
        login: loginReducer,
        register: registerReducer,
        flashSale: flashSaleReducer,
        featuredProducts: featuredProductsReducer,
        bestSellers: bestSellersReducer,
        categories: categoriesReducer,
        allProducts: allProductsReducer
    }
});

export default store;

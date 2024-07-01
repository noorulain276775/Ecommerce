// store/index.js
import { configureStore } from '@reduxjs/toolkit';
import sellerReducer from './slices/sellerSlice';

const store = configureStore({
    reducer: {
        seller: sellerReducer
    }
});

export default store;

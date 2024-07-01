// store/index.js
import { configureStore } from '@reduxjs/toolkit';
import sellerReducer from './slices/sellerSlice';
import loginReducer from './slices/loginSlice';

const store = configureStore({
    reducer: {
        seller: sellerReducer,
        login: loginReducer
    }
});

export default store;

// store/index.js
import { configureStore } from '@reduxjs/toolkit';
import sellerReducer from './slices/sellerSlice';
import loginReducer from './slices/loginSlice';
import registerReducer from './slices/registerSlice'

const store = configureStore({
    reducer: {
        seller: sellerReducer,
        login: loginReducer,
        register: registerReducer
    }
});

export default store;

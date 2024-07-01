// components/Home.js
import React from 'react';
import { useDispatch} from 'react-redux';
import { fetchSeller } from '../../store/slices/sellerSlice';
import { useNavigate } from 'react-router-dom';

export default function Home() {
    const dispatch = useDispatch();
    const navigate = useNavigate()

    const handleFetchSeller = () => {
        dispatch(fetchSeller());
        navigate('/seller');
    };

    return (
        <div>
            <button onClick={handleFetchSeller}>Seller</button>
        </div>
    );
}

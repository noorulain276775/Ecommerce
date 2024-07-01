import './App.css';
import Login from './components/Auth/Login/Login';
import Register from './components/Auth/Register/Register';
import ForgotPassword from './components/Auth/ForgotPassword/ForgotPassword';
import OTP from './components/Auth/OTPVerification/OTP';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/home/Home';
import Seller from './components/Sellers/Seller';

function App() {
  return (
    <Router>
      <Routes>
        <Route path='/register' element={<Register />} />
        <Route path='/login' element={<Login />} />
        <Route path='/forgot-password' element={<ForgotPassword />} />
        <Route path='/verify-otp' element={<OTP/>} />
        <Route path='' element={<Home/>} />
        <Route path='/seller' element={<Seller/>} />
        
      </Routes>
    </Router>
  );
}

export default App;
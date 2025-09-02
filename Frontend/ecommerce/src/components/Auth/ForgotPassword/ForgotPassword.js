import React, { useState } from "react";
import "../Login/Login.css";
import "../Register/Register.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import blueArrow from "../../../assets/images/Button.svg";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";

const ForgotPassword = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [phone, setPhone] = useState("");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handlePhoneNumberChange = (e) => {
    setPhone(e.target.value);
    setError("");
  };

  const validatePhone = () => {
    if (!phone.trim()) {
      setError("Phone number is required");
      return false;
    }
    if (!/^923[0-9]{9}$/.test(phone)) {
      setError("Please enter a valid Pakistani phone number (923xxxxxxxxx)");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validatePhone()) {
      return;
    }
    
    setStatus("loading");
    setError("");
    
    try {
      const response = await fetch('http://127.0.0.1:8000/accounts/forgot-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone }),
      });
      
      if (response.ok) {
        setSuccess(true);
        setStatus("success");
        // Navigate to OTP verification after 2 seconds
        setTimeout(() => {
          navigate("/verify-otp", { state: { phone } });
        }, 2000);
      } else {
        const data = await response.json();
        setError(data.message || "Failed to send OTP. Please try again.");
        setStatus("error");
      }
    } catch (error) {
      setError("Network error. Please check your connection and try again.");
      setStatus("error");
    }
  };

  return (
    <div className="login-container">
      <div className="loginform-container">
        <div className="header-image">
          <img src={headerImage} alt="Header" className="bubbles" />
          <div className="logo">
            <img src={logo} alt="Shopee" />
          </div>
        </div>
        
        <div className="form-content">
          <h1 className="create-account">Reset Password</h1>
          <p className="slogan-login">Don't worry, we'll help you reset it!</p>
          
          {success ? (
            <div className="success-message">
              <div className="success-icon">✓</div>
              <h3>OTP Sent Successfully!</h3>
              <p>We've sent a verification code to {phone}</p>
              <p>Redirecting to verification...</p>
            </div>
          ) : (
            <>
              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}
              
              <form className="form-login" onSubmit={handleSubmit}>
                <div className="input-group">
                  <input
                    onChange={handlePhoneNumberChange}
                    className={`login-input ${error ? 'error' : ''}`}
                    id="phone"
                    placeholder="Enter your phone number (923xxxxxxxxx)"
                    value={phone}
                    required
                  />
                </div>
                
                <button 
                  className="login-button2" 
                  type="submit"
                  disabled={status === "loading"}
                >
                  {status === "loading" ? (
                    <>
                      <span className="loading-spinner"></span>
                      Sending OTP...
                    </>
                  ) : (
                    "Send OTP"
                  )}
                </button>
                
                <div className="next-step-container">
                  <p className="login-question2">Remember your password?</p>
                  <Link to={"/login"}>
                    <img
                      src={blueArrow}
                      alt="Sign In"
                      className="blue-arrow"
                    />
                  </Link>
                </div>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;

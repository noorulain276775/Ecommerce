import React, { useState, useRef, useEffect } from "react";
import "../Login/Login.css";
import "../Register/Register.css";
import "./OTP.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import blueArrow from "../../../assets/images/Button.svg";
import { Link, useNavigate, useLocation } from "react-router-dom";

const OTP = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [otp, setOtp] = useState(new Array(6).fill(""));
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes
  const [canResend, setCanResend] = useState(false);
  const inputs = useRef([]);
  
  const phone = location.state?.phone || "";

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setCanResend(true);
    }
  }, [timeLeft]);

  const handleChange = (element, index) => {
    const value = element.value;
    if (/^[0-9]$/.test(value)) {
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);
      setError("");
      
      if (index < 5) {
        inputs.current[index + 1].focus();
      } else {
        // Auto-submit when all fields are filled
        const otpString = newOtp.join("");
        if (otpString.length === 6) {
          handleSubmit(otpString);
        }
      }
    } else {
      element.value = "";
    }
  };

  const handleBackspace = (event, index) => {
    if (event.keyCode === 8 && index > 0 && !otp[index]) {
      inputs.current[index - 1].focus();
    }
  };

  const handleSubmit = async (otpCode = null) => {
    const code = otpCode || otp.join("");
    
    if (code.length !== 6) {
      setError("Please enter the complete 6-digit OTP");
      return;
    }
    
    setStatus("loading");
    setError("");
    
    try {
      const response = await fetch('http://127.0.0.1:8000/accounts/verify-otp/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone, otp: code }),
      });
      
      if (response.ok) {
        setStatus("success");
        // Navigate to reset password page
        setTimeout(() => {
          navigate("/reset-password", { state: { phone, verified: true } });
        }, 1500);
      } else {
        const data = await response.json();
        setError(data.message || "Invalid OTP. Please try again.");
        setStatus("error");
        // Clear OTP on error
        setOtp(new Array(6).fill(""));
        inputs.current[0].focus();
      }
    } catch (error) {
      setError("Network error. Please check your connection and try again.");
      setStatus("error");
    }
  };

  const handleResendOTP = async () => {
    setStatus("loading");
    setError("");
    
    try {
      const response = await fetch('http://127.0.0.1:8000/accounts/resend-otp/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone }),
      });
      
      if (response.ok) {
        setTimeLeft(300);
        setCanResend(false);
        setOtp(new Array(6).fill(""));
        inputs.current[0].focus();
      } else {
        const data = await response.json();
        setError(data.message || "Failed to resend OTP. Please try again.");
      }
    } catch (error) {
      setError("Network error. Please try again.");
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
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
          <h1 className="create-account">Verify Your Phone</h1>
          <p className="slogan-login">
            We've sent a 6-digit code to {phone ? `****${phone.slice(-4)}` : 'your phone'}
          </p>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <div className="otp-verification">
            <div className="otp-inputs">
              {otp.map((data, index) => (
                <input
                  key={index}
                  type="text"
                  maxLength="1"
                  value={data}
                  onChange={(e) => handleChange(e.target, index)}
                  onKeyDown={(e) => handleBackspace(e, index)}
                  ref={(el) => (inputs.current[index] = el)}
                  className={`otp-input ${error ? 'error' : ''}`}
                  disabled={status === "loading"}
                />
              ))}
            </div>
            
            <div className="timer-container">
              {!canResend ? (
                <p className="timer-text">
                  Resend OTP in {formatTime(timeLeft)}
                </p>
              ) : (
                <button 
                  className="resend-button" 
                  onClick={handleResendOTP}
                  disabled={status === "loading"}
                >
                  Resend OTP
                </button>
              )}
            </div>
            
            <button 
              className="otp-submit" 
              onClick={() => handleSubmit()}
              disabled={status === "loading" || otp.join("").length !== 6}
            >
              {status === "loading" ? (
                <>
                  <span className="loading-spinner"></span>
                  Verifying...
                </>
              ) : (
                "Verify OTP"
              )}
            </button>
            
            <div className="next-step-container">
              <p className="login-question2">Wrong number?</p>
              <Link to={"/forgot-password"}>
                <img
                  src={blueArrow}
                  alt="Go Back"
                  className="blue-arrow"
                />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OTP;

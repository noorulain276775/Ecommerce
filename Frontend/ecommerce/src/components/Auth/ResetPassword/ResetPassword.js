import React, { useState } from "react";
import "../Login/Login.css";
import "../Register/Register.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import blueArrow from "../../../assets/images/Button.svg";
import { Link, useNavigate, useLocation } from "react-router-dom";

const ResetPassword = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  
  const phone = location.state?.phone || "";
  const verified = location.state?.verified || false;

  // Redirect if not verified
  React.useEffect(() => {
    if (!verified) {
      navigate("/forgot-password");
    }
  }, [verified, navigate]);

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
    setError("");
  };

  const handleConfirmPasswordChange = (e) => {
    setConfirmPassword(e.target.value);
    setError("");
  };

  const validatePasswords = () => {
    if (!password.trim()) {
      setError("Password is required");
      return false;
    }
    
    if (password.length < 8) {
      setError("Password must be at least 8 characters long");
      return false;
    }
    
    if (!/(?=.*[A-Z])(?=.*[\W_])/.test(password)) {
      setError("Password must contain at least one uppercase letter and one special character");
      return false;
    }
    
    if (!confirmPassword.trim()) {
      setError("Please confirm your password");
      return false;
    }
    
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validatePasswords()) {
      return;
    }
    
    setStatus("loading");
    setError("");
    
    try {
      const response = await fetch('http://127.0.0.1:8000/accounts/reset-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone, password }),
      });
      
      if (response.ok) {
        setSuccess(true);
        setStatus("success");
        // Navigate to login after 3 seconds
        setTimeout(() => {
          navigate("/login");
        }, 3000);
      } else {
        const data = await response.json();
        setError(data.message || "Failed to reset password. Please try again.");
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
          <p className="slogan-login">Create a new password for your account</p>
          
          {success ? (
            <div className="success-message">
              <div className="success-icon">✓</div>
              <h3>Password Reset Successfully!</h3>
              <p>Your password has been updated successfully.</p>
              <p>Redirecting to login...</p>
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
                    onChange={handlePasswordChange}
                    className={`login-input ${error ? 'error' : ''}`}
                    id="password"
                    type="password"
                    placeholder="Enter your new password"
                    value={password}
                    required
                  />
                </div>
                
                <div className="input-group">
                  <input
                    onChange={handleConfirmPasswordChange}
                    className={`login-input ${error ? 'error' : ''}`}
                    id="confirm_password"
                    type="password"
                    placeholder="Confirm your new password"
                    value={confirmPassword}
                    required
                  />
                </div>
                
                <div className="password-requirements">
                  <p className="requirements-title">Password must contain:</p>
                  <ul className="requirements-list">
                    <li className={password.length >= 8 ? 'valid' : ''}>
                      At least 8 characters
                    </li>
                    <li className={/(?=.*[A-Z])/.test(password) ? 'valid' : ''}>
                      One uppercase letter
                    </li>
                    <li className={/(?=.*[\W_])/.test(password) ? 'valid' : ''}>
                      One special character
                    </li>
                    <li className={password === confirmPassword && confirmPassword ? 'valid' : ''}>
                      Passwords match
                    </li>
                  </ul>
                </div>
                
                <button 
                  className="login-button2" 
                  type="submit"
                  disabled={status === "loading"}
                >
                  {status === "loading" ? (
                    <>
                      <span className="loading-spinner"></span>
                      Updating Password...
                    </>
                  ) : (
                    "Update Password"
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

export default ResetPassword;

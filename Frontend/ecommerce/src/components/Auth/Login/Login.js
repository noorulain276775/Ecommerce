import React, { useState } from "react";
import "./Login.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import blueArrow from "../../../assets/images/Button.svg";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { doLogin } from "../../../store/slices/loginSlice";

const Login = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { status, error } = useSelector((state) => state.login);
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");

  const handlePhoneNumberChange = (e) => {
    setPhone(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const data = {
    phone,
    password,
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const resultAction = await dispatch(doLogin(data));
      if (doLogin.fulfilled.match(resultAction)) {
        navigate("/");
      }
    } catch (error) {
      console.error("Login failed:", error);
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
          <h1 className="create-account">Welcome Back</h1>
          <p className="slogan-login">Sign in to your account</p>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <form className="form-login" onSubmit={handleSubmit}>
            <div className="input-group">
              <input
                onChange={handlePhoneNumberChange}
                className="login-input"
                id="phone"
                name="phone"
                type="tel"
                placeholder="Enter your phone number"
                value={phone}
                required
              />
            </div>
            
            <div className="input-group">
              <input
                onChange={handlePasswordChange}
                className="login-input"
                id="password"
                name="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                required
              />
            </div>
            
            <Link to={"/forgot-password"} className="forgot-password">
              Forgot your password?
            </Link>
            
            <button className="login-button2" type="submit" disabled={status === "loading"}>
              {status === "loading" ? (
                <>
                  <span className="loading-spinner"></span>
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </button>
            
            <div className="next-step-container">
              <p className="login-question2">Don't have an account?</p>
              <Link to={"/register"}>
                <img
                  src={blueArrow}
                  alt="Sign Up"
                  className="blue-arrow"
                />
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;

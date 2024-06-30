import React, { useState } from "react";
import "./Login.css";
import "../Register/Register.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import blueArrow from "../../../assets/images/Button.svg";
import { Link } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { authActions } from "../../../store/authSlice";

const Login = () => {
  const isLoggedIn = useSelector(state => state.auth.isLoggedIn);
  console.log(isLoggedIn)
  const dispatch = useDispatch()
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");

  const handlePhoneNumberChange = (e) => {
    setPhone(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(phone)
    dispatch(authActions.login())
  };

  return (
    <div className="login-container">
      <div className="loginform-container">
        <div className="header-image">
          <img src={headerImage} alt="Header" className="bubbles" />
        </div>
        <div className="logo">
          <img src={logo} alt="Shopee" />
        </div>
        <h1 className="create-account">Login</h1>
        <p className="slogan-login">Good to see you back</p>
        <form className="form-login" onSubmit={handleSubmit}>
          <input
            onChange={handlePhoneNumberChange}
            className="login-input"
            id="phone"
            placeholder="Phone number"
            value={phone}
            required
          />
          <input
            onChange={handlePasswordChange}
            className="login-input"
            id="password"
            type="password"
            placeholder="Password"
            value={password}
            required
          />
          <Link to={"/forgot-password"}>
            <p className="forgot-password">Forgot Password?</p>
          </Link>
          <button className="login-button2" type="submit">
            Login
          </button>
          <div className="next-step-container">
            <p className="login-question2">Don't have account?</p>
            <Link to={"/register"}>
              <img
                src={blueArrow}
                alt="Next Step"
                className="blue-arrow"
                style={{ cursor: "pointer" }}
              />
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;

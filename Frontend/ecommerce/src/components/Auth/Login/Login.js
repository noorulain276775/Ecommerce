import React, { useState } from "react";
import "./Login.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import blueArrow from "../../../assets/images/Button.svg";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { doLogin } from "../../../store/slices/loginSlice";

const Login = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
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
        navigate("/seller");
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
            name="phone"
            type="tel"
            placeholder="Phone number"
            value={phone}
            required
          />
          <input
            onChange={handlePasswordChange}
            className="login-input"
            id="password"
            name="password"
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
            <p className="login-question2">Don't have an account?</p>
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

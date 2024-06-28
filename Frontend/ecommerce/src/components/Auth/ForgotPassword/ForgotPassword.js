import React, { useState } from "react";
import "../Login/Login.css";
import "../Register/Register.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import blueArrow from "../../../assets/images/Button.svg";
import { Link } from "react-router-dom";

const ForgotPassword = () => {
  const [phone, setPhone] = useState("");

  const handlePhoneNumberChange = (e) => {
    setPhone(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(phone);
  };

  return (
    <div className="login-container">
      <div className="loginform-container">
        <div className="header-image additional">
          <img src={headerImage} alt="Header" className="bubbles2" />
        </div>
        <div className="logo">
          <img src={logo} alt="Shopee" />
        </div>
        <h1 className="create-account">Reset Password</h1>
        <p className="slogan-login">Don't worry, we'll help you reset it!</p>
        <form className="form-login" onSubmit={handleSubmit}>
          <input
            onChange={handlePhoneNumberChange}
            className="login-input"
            id="phone"
            placeholder="Enter you Phone number"
            value={phone}
          />

          <Link to={"/verify-otp"}>
            <button className="login-button2" type="submit">
              Submit
            </button>
          </Link>
          <div className="next-step-container">
            <p className="login-question2">Remember Password? Go back</p>
            <Link to={"/login"}>
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

export default ForgotPassword;

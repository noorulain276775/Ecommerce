import React, { useState } from "react";
import "../Login/Login.css";
import "./Register.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import blueArrow from "../../../assets/images/Button.svg";
import { Link } from "react-router-dom";

const Register = () => {
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [step, setStep] = useState(1);

  const handleConfirmPasswordChange = (e) => {
    setConfirmPassword(e.target.value);
  };

  const handleFirstNameChange = (e) => {
    setFirstName(e.target.value);
  };

  const handleLastNameChange = (e) => {
    setLastName(e.target.value);
  };

  const handlePhoneNumberChange = (e) => {
    setPhone(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(phone);
    console.log(password);
    console.log(confirmPassword);
    console.log(firstName);
    console.log(lastName);
  };

  const handleNextStep = () => {
    setStep(2);
  };

  const handleBackStep = () => {
    setStep(1);
  };
  return (
    <div className="login-container">
      <div className="loginform-container">
        <div className="header-image">
          <img src={headerImage} alt="Header" className="bubbles"/>
        </div>
        <div className="logo">
          <img src={logo} alt="Shopee" />
        </div>
        <h1 className="create-account">Create Account</h1>
        
        <form className="form-login" onSubmit={handleSubmit}>
          {step === 1 && (
            <>
            <p className="slogan-login">Welcome to Our eCommerce Platform!</p>
              <input
                onChange={handlePhoneNumberChange}
                className="login-input"
                id="phone"
                placeholder="Phone number"
                value={phone}
              />
              <input
                onChange={handlePasswordChange}
                className="login-input"
                id="password"
                type="password"
                placeholder="Password"
                value={password}
              />
              <input
                onChange={handleConfirmPasswordChange}
                className="login-input"
                id="confirm_password"
                type="password"
                placeholder="Confirm Password"
                value={confirmPassword}
              />
              <button
                onClick={handleNextStep}
                className="login-button2"
                type="submit"
              >
                Next
              </button>
              <div className="next-step-container">
                <p className="login-question2">Already have an account?</p>
                <Link to={'/login'}>
                  <img
                    src={blueArrow}
                    alt="Next Step"
                    className="blue-arrow"
                    style={{ cursor: "pointer" }}
                  />
                </Link>
              </div>
            </>
          )}
          {step === 2 && (
            <>
              <p className="slogan-login">We would love to know your name</p>
              <input
                onChange={handleFirstNameChange}
                className="login-input"
                id="first_name"
                placeholder="First Name"
                value={firstName}
              />
              <input
                onChange={handleLastNameChange}
                className="login-input"
                id="last_name"
                placeholder="Last Name"
                value={lastName}
              />
              <button
                onClick={handleBackStep}
                className="login-button2"
                type="submit"
              >
                Go Back
              </button>
              <button className="login-button" type="submit">
                Register
              </button>
            </>
          )}
        </form>
      </div>
    </div>
  );
};

export default Register;

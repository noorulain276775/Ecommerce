import React, { useState, useRef } from "react";
import "../Login/Login.css";
import "../Register/Register.css";
import "./OTP.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import { Link } from "react-router-dom";

const OTP = () => {
  const [otp, setOtp] = useState(new Array(6).fill(""));
  const inputs = useRef([]);

  const handleChange = (element, index) => {
    const value = element.value;
    if (/^[0-9]$/.test(value)) {
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);
      if (index < 5) {
        inputs.current[index + 1].focus();
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

  //   const handleSubmit = (e) => {
  //     e.preventDefault();
  //     console.log(phone);
  //     console.log(password);
  //   };

  return (
    <div className="login-container">
      <div className="loginform-container">
        <div className="header-image additional">
          <img src={headerImage} alt="Header" className="bubbles" />
        </div>
        <div className="logo">
          <img src={logo} alt="Shopee" />
        </div>
        <h1 className="create-account">Enter Your OTP</h1>
        <p className="slogan-login">We've sent the OTP on your phone number!</p>
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
              />
            ))}
          </div>
          <button className="otp-submit" type="submit">
            Submit
          </button>
            <button className="otp-submit cancel" type="submit">
              Cancel
            </button>
          <Link to={"/resend-otp"}>
            <p className="otp-resend">Didn't receive otp? resend again</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default OTP;

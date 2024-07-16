import React, { useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "../Login/Login.css";
import "./Register.css";
import logo from "../../../assets/images/logo.svg";
import headerImage from "../../../assets/images/Bubbles.png";
import blueArrow from "../../../assets/images/Button.svg";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";

const Register = () => {
  const navigate = useNavigate();
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState(null);
  // const [photo, setPhoto] = useState(null);
  const [step, setStep] = useState(1);
  const [dateError, setDateError] = useState("");

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

  const handleDateOfBirthChange = (date) => {
    setDateOfBirth(date);
    const today = new Date();
    const minDate = new Date(today.getFullYear() - 10, today.getMonth(), today.getDate());
    if (date > minDate) {
      setDateError("You must be at least 10 years old.");
    } else {
      setDateError("");
    }
  };

  // const handlePhotoChange = (e) => {
  //   setPhoto(e.target.files[0]);
  // };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // try {
    //   const resultAction = await dispatch(doLogin(data));
    //   if (doLogin.fulfilled.match(resultAction)) {
    //     navigate("/seller");
    //   }
    // } catch (error) {
    //   console.error("Login failed:", error);
    // }
  };

  const handleNextStep = () => {
    setStep(2);
  };

  const handleBackStep = () => {
    setStep(1);
  };

  const getMaxDate = () => {
    const today = new Date();
    return new Date(today.getFullYear() - 10, today.getMonth(), today.getDate());
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
                type="button"
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
              <DatePicker
                selected={dateOfBirth}
                onChange={handleDateOfBirthChange}
                className="login-input date-pick"
                id="date_of_birth"
                placeholderText="Select date of birth (optional)"
                dateFormat="yyyy-MM-dd"
                showYearDropdown
                showMonthDropdown
                dropdownMode="select"
                maxDate={getMaxDate()}
              />
              {dateError && <p className="error-message">{dateError}</p>}
              {/* <input
                onChange={handlePhotoChange}
                className="login-input"
                id="photo"
                type="file"
              /> */}
              <button
                onClick={handleBackStep}
                className="login-button2"
                type="button"
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

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
import { doRegister } from "../../../store/slices/registerSlice";
import { useDispatch } from "react-redux";

const Register = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setpassword2] = useState("");
  const [first_name, setfirst_name] = useState("");
  const [last_name, setlast_name] = useState("");
  const [dateOfBirth, setdateOfBirth] = useState(null);
  // const [photo, setPhoto] = useState(null);


  const [step, setStep] = useState(1);
  const [dateError, setDateError] = useState("");

  const handlepassword2Change = (e) => {
    setpassword2(e.target.value);
  };

  const handlefirst_nameChange = (e) => {
    setfirst_name(e.target.value);
  };

  const handlelast_nameChange = (e) => {
    setlast_name(e.target.value);
  };

  const handlePhoneNumberChange = (e) => {
    setPhone(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handledateOfBirthChange = (date) => {
    setdateOfBirth(date);
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

  const data = {
    phone,
    password,
    first_name,
    last_name,
    dateOfBirth,
    password2,
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const resultAction = await dispatch(doRegister(data));
      if (doRegister.fulfilled.match(resultAction)) {
        navigate("/login");
      }
    } catch (error) {
      console.error("Registration failed:", error);
    }
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
                onChange={handlepassword2Change}
                className="login-input"
                id="confirm_password"
                type="password"
                placeholder="Confirm Password"
                value={password2}
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
                onChange={handlefirst_nameChange}
                className="login-input"
                id="first_name"
                placeholder="First Name"
                value={first_name}
              />
              <input
                onChange={handlelast_nameChange}
                className="login-input"
                id="last_name"
                placeholder="Last Name"
                value={last_name}
              />
              <DatePicker
                selected={dateOfBirth}
                onChange={handledateOfBirthChange}
                className="login-input date-pick"
                id="dateOfBirth"
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

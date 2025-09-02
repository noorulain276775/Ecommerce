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
import { useDispatch, useSelector } from "react-redux";

const Register = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { status, error } = useSelector((state) => state.register);
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setpassword2] = useState("");
  const [first_name, setfirst_name] = useState("");
  const [last_name, setlast_name] = useState("");
  const [dateOfBirth, setdateOfBirth] = useState(null);
  const [step, setStep] = useState(1);
  const [dateError, setDateError] = useState("");
  const [validationErrors, setValidationErrors] = useState({});

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

  const validateStep1 = () => {
    const errors = {};
    
    if (!phone.trim()) {
      errors.phone = "Phone number is required";
    } else if (!/^923[0-9]{9}$/.test(phone)) {
      errors.phone = "Please enter a valid Pakistani phone number (923xxxxxxxxx)";
    }
    
    if (!password.trim()) {
      errors.password = "Password is required";
    } else if (password.length < 8) {
      errors.password = "Password must be at least 8 characters long";
    } else if (!/(?=.*[A-Z])(?=.*[\W_])/.test(password)) {
      errors.password = "Password must contain at least one uppercase letter and one special character";
    }
    
    if (!password2.trim()) {
      errors.password2 = "Please confirm your password";
    } else if (password !== password2) {
      errors.password2 = "Passwords do not match";
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateStep2 = () => {
    const errors = {};
    
    if (!first_name.trim()) {
      errors.first_name = "First name is required";
    } else if (!/^[a-zA-Z]+$/.test(first_name)) {
      errors.first_name = "First name must contain only letters";
    }
    
    if (!last_name.trim()) {
      errors.last_name = "Last name is required";
    } else if (!/^[a-zA-Z]+$/.test(last_name)) {
      errors.last_name = "Last name must contain only letters";
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep2()) {
      return;
    }
    
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
    if (validateStep1()) {
      setStep(2);
      setValidationErrors({});
    }
  };

  const handleBackStep = () => {
    setStep(1);
    setValidationErrors({});
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
          <div className="logo">
            <img src={logo} alt="Shopee" />
          </div>
        </div>
        
        <div className="form-content">
          <h1 className="create-account">Create Account</h1>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <form className="form-login" onSubmit={handleSubmit}>
            {step === 1 && (
              <>
                <p className="slogan-login">Welcome to Our eCommerce Platform!</p>
                
                <div className="input-group">
                  <input
                    onChange={handlePhoneNumberChange}
                    className={`login-input ${validationErrors.phone ? 'error' : ''}`}
                    id="phone"
                    placeholder="Enter your phone number (923xxxxxxxxx)"
                    value={phone}
                    required
                  />
                  {validationErrors.phone && (
                    <span className="field-error">{validationErrors.phone}</span>
                  )}
                </div>
                
                <div className="input-group">
                  <input
                    onChange={handlePasswordChange}
                    className={`login-input ${validationErrors.password ? 'error' : ''}`}
                    id="password"
                    type="password"
                    placeholder="Create a strong password"
                    value={password}
                    required
                  />
                  {validationErrors.password && (
                    <span className="field-error">{validationErrors.password}</span>
                  )}
                </div>
                
                <div className="input-group">
                  <input
                    onChange={handlepassword2Change}
                    className={`login-input ${validationErrors.password2 ? 'error' : ''}`}
                    id="confirm_password"
                    type="password"
                    placeholder="Confirm your password"
                    value={password2}
                    required
                  />
                  {validationErrors.password2 && (
                    <span className="field-error">{validationErrors.password2}</span>
                  )}
                </div>
                
                <button
                  onClick={handleNextStep}
                  className="login-button2"
                  type="button"
                >
                  Continue
                </button>
                
                <div className="next-step-container">
                  <p className="login-question2">Already have an account?</p>
                  <Link to={'/login'}>
                    <img
                      src={blueArrow}
                      alt="Sign In"
                      className="blue-arrow"
                    />
                  </Link>
                </div>
              </>
            )}
            
            {step === 2 && (
              <>
                <p className="slogan-login">Tell us a bit about yourself</p>
                
                <div className="input-group">
                  <input
                    onChange={handlefirst_nameChange}
                    className={`login-input ${validationErrors.first_name ? 'error' : ''}`}
                    id="first_name"
                    placeholder="Enter your first name"
                    value={first_name}
                    required
                  />
                  {validationErrors.first_name && (
                    <span className="field-error">{validationErrors.first_name}</span>
                  )}
                </div>
                
                <div className="input-group">
                  <input
                    onChange={handlelast_nameChange}
                    className={`login-input ${validationErrors.last_name ? 'error' : ''}`}
                    id="last_name"
                    placeholder="Enter your last name"
                    value={last_name}
                    required
                  />
                  {validationErrors.last_name && (
                    <span className="field-error">{validationErrors.last_name}</span>
                  )}
                </div>
                
                <div className="input-group">
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
                  {dateError && <span className="field-error">{dateError}</span>}
                </div>
                
                <div className="button-group">
                  <button
                    onClick={handleBackStep}
                    className="login-button2 secondary"
                    type="button"
                  >
                    Back
                  </button>
                  <button 
                    className="login-button2" 
                    type="submit"
                    disabled={status === "loading"}
                  >
                    {status === "loading" ? (
                      <>
                        <span className="loading-spinner"></span>
                        Creating Account...
                      </>
                    ) : (
                      "Create Account"
                    )}
                  </button>
                </div>
              </>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;

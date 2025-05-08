import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";

const OtpScreen = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [otpValues, setOtpValues] = useState(Array(6).fill(""));
  const otpInputs = useRef([]);
  const navigate = useNavigate();
  const location = useLocation();

  const queryParams = new URLSearchParams(location.search);
  const email =
    location.state?.email ||
    queryParams.get("email") ||
    localStorage.getItem("signup_email") ||
    "";
  const password =
    location.state?.password ||
    queryParams.get("password") ||
    localStorage.getItem("signup_password") ||
    "";
  const username =
    location.state?.username ||
    queryParams.get("username") ||
    localStorage.getItem("signup_username") ||
    "";

  useEffect(() => {
    if (otpInputs.current[0]) {
      otpInputs.current[0].focus();
    }
  }, []);

  const handleChange = (e, index) => {
    const value = e.target.value;
    if (value && !/^\d+$/.test(value)) return;
    const newOtpValues = [...otpValues];
    newOtpValues[index] = value.slice(0, 1);
    setOtpValues(newOtpValues);
    if (value && index < 5) {
      otpInputs.current[index + 1].focus();
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === "Backspace" && !otpValues[index] && index > 0) {
      otpInputs.current[index - 1].focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").trim();
    if (/^\d+$/.test(pastedData)) {
      const pastedOtp = pastedData.slice(0, 6).split("");
      const newOtpValues = [...otpValues];
      pastedOtp.forEach((digit, idx) => {
        if (idx < 6) newOtpValues[idx] = digit;
      });
      setOtpValues(newOtpValues);
      const nextEmptyIndex = newOtpValues.findIndex((val) => !val);
      otpInputs.current[nextEmptyIndex === -1 ? 5 : nextEmptyIndex].focus();
    }
  };

  const getOtpCode = () => otpValues.join("");

  const resendOtp = async () => {
    if (!email || !password || !username) {
      alert("Missing registration information");
      return;
    }
    setIsLoading(true);
    try {
      await axios.post("http://127.0.0.1:8000/auth/signup/", {
        email,
        password,
        username,
      });
      alert("OTP resent successfully");
    } catch (error) {
      alert(error.response?.data?.error || "Failed to resend OTP");
    } finally {
      setIsLoading(false);
    }
  };

  const verifyOtp = async () => {
    const otpCode = getOtpCode();
    if (otpCode.length !== 6) return alert("Please enter the complete OTP");
    setIsLoading(true);
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/auth/verify-otp/",
        {
          username,
          email,
          otp: otpCode,
          password,
        }
      );
      const tempToken = response.data.temp_token;
      if (!tempToken) throw new Error("Empty token received from server");
      localStorage.setItem("temp_token", tempToken);
      navigate(`/roles?token=${encodeURIComponent(tempToken)}`);
    } catch (error) {
      alert(error.response?.data?.error || error.message || "Unknown error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container-fluid min-vh-100 d-flex flex-column flex-md-row p-0">
      {/* Left Panel */}
      <div className="col-md-6 d-flex flex-column justify-content-center align-items-center bg-white px-4 py-5">
        <div className="w-100" style={{ maxWidth: "400px" }}>
          <h1 className="mb-3 fw-bold text-dark">OTP Verification</h1>
          <p className="text-muted mb-4">
            We’ve sent a verification code to <strong>{email}</strong>
          </p>

          <div className="d-flex justify-content-between mb-4">
            {[0, 1, 2, 3, 4, 5].map((index) => (
              <input
                key={index}
                ref={(el) => (otpInputs.current[index] = el)}
                type="text"
                maxLength={1}
                className="form-control text-center mx-1"
                style={{ width: "50px", height: "50px", fontSize: "20px" }}
                value={otpValues[index]}
                onChange={(e) => handleChange(e, index)}
                onKeyDown={(e) => handleKeyDown(e, index)}
                onPaste={handlePaste}
                disabled={isLoading}
              />
            ))}
          </div>

          <button
            onClick={verifyOtp}
            disabled={isLoading}
            className="btn btn-success w-100 mb-3"
          >
            {isLoading ? (
              <span
                className="spinner-border spinner-border-sm"
                role="status"
                aria-hidden="true"
              ></span>
            ) : (
              "Verify"
            )}
          </button>

          <div className="text-center">
            <span>Didn't receive the code?</span>
            <button
              onClick={resendOtp}
              disabled={isLoading}
              className="btn btn-link text-success fw-bold"
            >
              Resend
            </button>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div className="col-md-6 d-none d-md-flex bg-success bg-opacity-25 justify-content-center align-items-center">
        <img
          src="/enter-otp.svg"
          alt="OTP Illustration"
          className="img-fluid"
          style={{ maxWidth: "70%" }}
        />
      </div>
    </div>
  );
};

export default OtpScreen;
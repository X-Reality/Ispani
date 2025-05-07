import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';

const OtpScreen = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [otpValues, setOtpValues] = useState(Array(6).fill(''));
  const otpInputs = useRef([]);
  const navigate = useNavigate();
  const location = useLocation();

  // Get parameters from URL or location state
  const queryParams = new URLSearchParams(location.search);
  const email = location.state?.email || queryParams.get('email') || localStorage.getItem('signup_email') || '';
  const password = location.state?.password || queryParams.get('password') || localStorage.getItem('signup_password') || '';
  const username = location.state?.username || queryParams.get('username') || localStorage.getItem('signup_username') || '';


  useEffect(() => {
    // Focus the first input field when component mounts
    if (otpInputs.current[0]) {
      otpInputs.current[0].focus();
    }
  }, []);

  const handleChange = (e, index) => {
    const value = e.target.value;
    
    // Only allow numbers
    if (value && !/^\d+$/.test(value)) return;

    // Update the OTP values array
    const newOtpValues = [...otpValues];
    newOtpValues[index] = value.slice(0, 1); // Only take the first character
    setOtpValues(newOtpValues);

    // Move focus to next input if a number was entered
    if (value && index < 5) {
      otpInputs.current[index + 1].focus();
    }
  };

  const handleKeyDown = (e, index) => {
    // Move focus to previous input on backspace if current input is empty
    if (e.key === 'Backspace' && !otpValues[index] && index > 0) {
      otpInputs.current[index - 1].focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim();
    
    // Check if pasted data is a number and has the expected length
    if (/^\d+$/.test(pastedData)) {
      const pastedOtp = pastedData.slice(0, 6).split('');
      const newOtpValues = [...otpValues];
      
      pastedOtp.forEach((digit, idx) => {
        if (idx < 6) {
          newOtpValues[idx] = digit;
        }
      });
      
      setOtpValues(newOtpValues);
      
      // Focus the next empty input or the last one
      const nextEmptyIndex = newOtpValues.findIndex(val => !val);
      const focusIndex = nextEmptyIndex === -1 ? 5 : nextEmptyIndex;
      otpInputs.current[focusIndex].focus();
    }
  };

  const getOtpCode = () => {
    return otpValues.join('');
  };

  const resendOtp = async () => {
    if (!email || !password || !username) {
      alert('Missing registration information');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/auth/signup/', {
        email,
        password,
        username
      });

      alert('OTP resent successfully');
    } catch (error) {
      console.error('Error resending OTP:', error);
      alert(error.response?.data?.error || 'Failed to resend OTP');
    } finally {
      setIsLoading(false);
    }
  };

  const verifyOtp = async () => {
    const otpCode = getOtpCode();

    if (otpCode.length !== 6) {
      alert('Please enter the complete OTP');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/auth/verify-otp/', {
        username,
        email,
        otp: otpCode,
        password
      });

      console.log('OTP verification response:', response.data);
      
      // Extract the temp_token from the response
      const tempToken = response.data.temp_token;
      
      if (tempToken) {
        // Store token in localStorage for potential later use
        localStorage.setItem('temp_token', tempToken);
        
        // Redirect to roles selection page with token
        navigate(`/roles?token=${encodeURIComponent(tempToken)}`);
      } else {
        throw new Error('Empty token received from server');
      }
    } catch (error) {
      console.error('Error in OTP verification:', error);
      alert(error.response?.data?.error || error.message || 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <header className="bg-white p-4 shadow-sm">
        <h1 className="text-xl font-bold">OTP Verification</h1>
      </header>

      <main className="flex-1 p-6 max-w-md mx-auto w-full">
        <div className="mt-6">
          <h2 className="text-2xl font-bold">Verification Code</h2>
          <p className="text-gray-600 mt-2">
            We have sent the verification code to {email}
          </p>
        </div>

        <div className="mt-10">
          <div className="flex justify-between gap-2">
            {[0, 1, 2, 3, 4, 5].map((index) => (
              <input
                key={index}
                ref={(el) => (otpInputs.current[index] = el)}
                type="text"
                maxLength={1}
                className="w-12 h-12 text-center border border-gray-300 rounded-lg focus:border-green-600 focus:ring-1 focus:ring-green-600 focus:outline-none text-lg"
                value={otpValues[index]}
                onChange={(e) => handleChange(e, index)}
                onKeyDown={(e) => handleKeyDown(e, index)}
                onPaste={handlePaste}
                disabled={isLoading}
              />
            ))}
          </div>
        </div>

        <button
          onClick={verifyOtp}
          disabled={isLoading}
          className="mt-10 w-full h-12 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 disabled:bg-green-400 flex justify-center items-center"
        >
          {isLoading ? (
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            'Verify'
          )}
        </button>

        <div className="mt-6 text-center">
          <span>Didn't receive the code?</span>
          <button
            onClick={resendOtp}
            disabled={isLoading}
            className="ml-1 text-green-600 font-bold hover:text-green-700 disabled:text-green-400"
          >
            Resend
          </button>
        </div>
      </main>
    </div>
  );
};

export default OtpScreen;
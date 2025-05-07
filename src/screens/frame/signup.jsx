import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { Input } from "../../components/ui/input";
import { Button } from "../../components/ui/button";

const Signup = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      // Sign up the user
      const response = await axios.post("http://localhost:8000/auth/signup/", {
        username,
        email,
        password,
      });
      
      
      
      if (response.status === 200 || response.status === 201) {
        // Save data to localStorage
        localStorage.setItem('signup_email', email);
        localStorage.setItem('signup_username', username);
        localStorage.setItem('signup_password', password);

        // Redirect to OTP screen
        navigate('/otp');
      } else {
        throw new Error('Unexpected response from server');
      }
    } catch (error) {
      console.error('Signup error:', error);
      alert(error.response?.data?.error || error.message || 'Signup failed');
    } 
  };

  return (
    <div className="sign">
      <div className="container">
        <header className="d-flex justify-content-between align-items-center mt-2">
          <img alt="Logo" src="/assets/logo2.jpg" width="100px" />
          <Button variant="outline" className="btn btn-dark">
            <span className="font-weight-semibold text-white">Download</span>
          </Button>
        </header>

        <div className="row mt-5">
          <div className="col-md-6">
            <h2>Create an Account</h2>
            <p>Join us to access exclusive features and connect with others.</p>

            {error && <div className="alert alert-danger">{error}</div>}

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="username" className="form-label">Username</label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              <div className="mb-3">
                <label htmlFor="email" className="form-label">Email</label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div className="mb-3">
                <label htmlFor="password" className="form-label">Password</label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <div className="form-check mb-3">
                <input className="form-check-input" type="checkbox" id="termsCheck" required />
                <label className="form-check-label" htmlFor="termsCheck">
                  Agree to terms and conditions
                </label>
              </div>

              <Button 
                variant="outline" 
                className="btn btn-dark" 
                type="submit" 
                disabled={loading}
              >
                <span className="font-weight-semibold text-white">
                  {loading ? "Processing..." : "Sign Up"}
                </span>
              </Button>
            </form>

            <div className="or mt-4 mb-4">
              <span>OR</span>
            </div>

            <Button variant="outline" className="btn btn-outline-dark mb-3" disabled={loading}>
              <span className="font-weight-semibold">Sign Up with Google</span>
            </Button>
            <Button variant="outline" className="btn btn-outline-dark mb-5" disabled={loading}>
              <span className="font-weight-semibold">Sign Up with LinkedIn</span>
            </Button>

            <h6>
              Already have an account?{" "}
              <Link to="/login" className="signin-link">Sign in</Link>
            </h6>
          </div>

          <div className="col-md-6">
            <div className="box"></div>
            <img alt="Mockup" src="/assets/Spaniprototypemockup1.png" className="img-fluid" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
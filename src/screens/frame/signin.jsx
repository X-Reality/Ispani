import React, { useState } from "react";
import { Link } from "react-router-dom"; 
import { Input } from "../../components/ui/input";
import { Button } from "../../components/ui/button";

const Signin = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: ""
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: "" }); // clear error on change
  };

  const validate = () => {
    let newErrors = {};
    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      // Submit form (e.g. call API)
      console.log("Form submitted:", formData);
    }
  };

  return (
    <div className="sign">
      <div className="container">
        <header className="d-flex justify-content-between align-items-center mt-2">
          <img className="h-4" alt="Logo" src="/assets/logo2.jpg" width="100px" />
          <Button variant="outline" className="btn btn-dark">
            <span className="font-weight-semibold text-white">Download</span>
          </Button>
        </header>
        <div className="row mt-5">
          <div className="col-md-6">
            <h2>Sign In to Your Account</h2>
            <p>Welcome back! Please sign in to continue.</p>
            <form onSubmit={handleSubmit} noValidate>
              <div className="mb-3">
                <label htmlFor="email" className="form-label">Email</label>
                <Input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Enter your email"
                />
                {errors.email && (
                  <small className="text-danger">{errors.email}</small>
                )}
              </div>
              <div className="mb-3">
                <label htmlFor="password" className="form-label">Password</label>
                <Input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                />
                {errors.password && (
                  <small className="text-danger">{errors.password}</small>
                )}
              </div>
              <div className="mb-3">
                <Button type="submit" variant="outline" className="btn btn-dark">
                  <span className="font-weight-semibold text-white">Sign In</span>
                </Button>
              </div>
            </form>
            <div className="or mt-4 mb-4"><span>OR</span></div>
            <Button variant="outline" className="btn btn-outline-dark mb-3">
              <span className="font-weight-semibold">Sign in with Google</span>
            </Button>
            <Button variant="outline" className="btn btn-outline-dark mb-5">
              <span className="font-weight-semibold">Sign in with LinkedIn</span>
            </Button>
            <h6>
            Don’t have an account?{" "}
            <Link to="/" className="signin-link">Sign up</Link>
            </h6>
          </div>
          <div className="col-md-6">
            <div className="box"></div>
            <img
              className="h-4"
              alt="Mockup"
              src="/assets/Spaniprototypemockup1.png"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signin;

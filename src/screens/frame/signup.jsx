import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Input } from "../../components/ui/input";
import { Button } from "../../components/ui/button";

const Signup = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [tempToken, setTempToken] = useState("");

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const token = queryParams.get("token");
    if (token) {
      setTempToken(token);
      console.log("Temp Token from URL:", token);
    }
  }, [location]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!tempToken) {
      alert("Missing registration token");
      return;
    }

    // Save token to sessionStorage for future use
    sessionStorage.setItem('temp_registration_token', tempToken);
    
    // Redirect to MultiStepForm (roles) and pass token in query param
    navigate(`/roles?token=${tempToken}`);
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
            <h2>Create an Account</h2>
            <p>Lorem ipsum dolor sit, amet consectetur adipisicing elit.</p>
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="Name" className="form-label">Name</label>
                <Input id="Name" name="Name" placeholder="Please add Name" />
              </div>
              <div className="mb-3">
                <label htmlFor="Email">Email</label>
                <Input type="email" id="Email" name="Email" placeholder="Please add Email" />
              </div>
              <div className="mb-3">
                <label htmlFor="Password">Password</label>
                <Input type="password" id="Password" name="Password" placeholder="Please add Password" />
              </div>
              <div className="form-check mb-3">
                <input className="form-check-input" type="checkbox" id="invalidCheck" required />
                <label className="form-check-label" htmlFor="invalidCheck">
                  Agree to terms and conditions
                </label>
              </div>
              <div className="mb-3">
                <Button variant="outline" className="btn btn-dark" type="submit">
                  <span className="font-weight-semibold text-white">Sign Up</span>
                </Button>
              </div>
            </form>

            <div className="or mt-4 mb-4">
              <span>OR</span>
            </div>
            <Button variant="outline" className="btn btn-outline-dark mb-3">
              <span className="font-weight-semibold">Sign Up with google.com</span>
            </Button>
            <Button variant="outline" className="btn btn-outline-dark mb-5">
              <span className="font-weight-semibold">Sign Up with linked.com</span>
            </Button>
            <h6>
              Already have an account?{" "}
              <a href="/signin" className="signin-link">Sign in</a>
            </h6>
          </div>
          <div className="col-md-6">
            <div className="box"></div>
            <img className="h-4" alt="Mockup" src="/assets/Spaniprototypemockup1.png" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;

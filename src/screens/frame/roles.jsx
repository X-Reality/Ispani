import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "../../components/ui/button";

const Roles = () => {
  const [selectedRoles, setSelectedRoles] = useState([]);
  const [authToken, setAuthToken] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // First try to get token from location state (from signup)
    const stateToken = location.state?.token;
    
    if (stateToken) {
      localStorage.setItem("authToken", stateToken);
      setAuthToken(stateToken);
      console.log("Token saved from state:", stateToken);
    } else {
      // Then check URL params (for backward compatibility)
      const urlParams = new URLSearchParams(window.location.search);
      const urlToken = urlParams.get('token');
      
      if (urlToken) {
        localStorage.setItem("authToken", urlToken);
        setAuthToken(urlToken);
        console.log("Token saved from URL:", urlToken);
      } else {
        // Finally check for reg_token from signup process
        const regToken = localStorage.getItem("reg_token");
        if (regToken) {
          localStorage.setItem("authToken", regToken);
          setAuthToken(regToken);
          console.log("Token saved from registration:", regToken);
        } else {
          setError("No authentication token found. Please sign up first.");
        }
      }
    }
  }, [location]);

  const handleRoleChange = (role) => {
    setSelectedRoles((prev) => {
      if (prev.includes(role)) {
        return prev.filter((r) => r !== role);
      } else if (prev.length < 2) {
        return [...prev, role];
      } else {
        alert("You can only select up to 2 roles.");
        return prev;
      }
    });
  };

  const handleContinue = () => {
    if (selectedRoles.length === 0) {
      alert("Please select at least one role.");
      return;
    }

    // Get the token from state or localStorage
    let token = authToken;
    if (!token) {
      token = localStorage.getItem('authToken') || localStorage.getItem('reg_token');
    }
    
    if (!token) {
      alert("Authentication token is missing. Please try again.");
      navigate("/signup");
      return;
    }

    // Get the first role and navigate to the corresponding form
    const role = selectedRoles[0];
    navigate(`/sign${role.replace("_", "")}`, {
      state: { 
        token: token,
        remainingRoles: selectedRoles.slice(1) 
      },
    });
  };

  const roles = [
    { label: "Student", value: "upstudent", icon: "bx-user-circle" },
    { label: "Tutor", value: "tutor", icon: "bx-user-circle" },
    { label: "HS Student", value: "learner", icon: "bx-user-circle" },
    { label: "Service Provider", value: "service", icon: "bx-briefcase" },
    { label: "Job Seeker", value: "jobseeker", icon: "bx-briefcase" },
  ];

  return (
    <div className="role">
      <div className="container">
        <header className="d-flex justify-content-between align-items-center mt-2">
          <img className="h-4" alt="Logo" src="/assets/logo2.jpg" width="100px" />
          <Button variant="outline" className="btn btn-dark">
            <span className="font-weight-semibold text-white">Download</span>
          </Button>
        </header>

        {error && (
          <div className="alert alert-danger my-3">{error}</div>
        )}

        <div className="row">
          {/* Left Section - Progress */}
          <div className="col-md-6">
            <div className="box"></div>
            <div className="progress-container">
              <div className="progress-step active">
                <div className="circle"></div>
                <span>Choose Role</span>
              </div>
              <div className="progress-step">
                <div className="circle"></div>
                <span>Tell us about yourself</span>
              </div>
              <div className="progress-step">
                <div className="circle"></div>
                <span>Choose how you use the app</span>
              </div>
              <div className="progress-step">
                <div className="circle"></div>
                <span>Create An Account</span>
              </div>
              <div className="progress-step">
                <div className="circle"></div>
                <span>Create An Account</span>
              </div>
              <div className="progress-step">
                <div className="circle"></div>
                <span>Create An Account</span>
              </div>
            </div>
          </div>

          {/* Right Section - Role Cards */}
          <div className="col-md-6">
            <h4>Select one or two roles to continue:</h4>
            <div className="row">
              {roles.map((role, index) => (
                <div key={index} className="col-md-6 mb-3">
                  <div
                    className={`card role-card ${selectedRoles.includes(role.value) ? "selected" : ""}`}
                    onClick={() => handleRoleChange(role.value)}
                    style={{ cursor: "pointer", padding: "10px", textAlign: "center" }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedRoles.includes(role.value)}
                      onChange={() => {}}
                      style={{ display: "none" }}
                    />
                    <i className={`bx ${role.icon} bx-md mb-2`}></i>
                    <h6>{role.label}</h6>
                  </div>
                </div>
              ))}
            </div>

            <Button 
              onClick={handleContinue} 
              className="btn btn-primary mt-3"
              disabled={!authToken || selectedRoles.length === 0}
            >
              Continue
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Roles;
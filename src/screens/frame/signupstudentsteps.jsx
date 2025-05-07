import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";

const MultiStepForm = () => {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();
  const location = useLocation();

  // Get token and remaining roles from location state
  const { token, remainingRoles = [] } = location.state || {};
  const [roles, setRoles] = useState(remainingRoles);
  const [authToken, setAuthToken] = useState(token);
  const [formError, setFormError] = useState("");

  // Form state
  const [role, setRole] = useState("student");
  const [city, setCity] = useState("");
  const [yearOfStudy, setYearOfStudy] = useState(null);
  const [course, setCourse] = useState("");
  const [hobbies, setHobbies] = useState([]);
  const [qualification, setQualification] = useState("");
  const [institution, setInstitution] = useState("");

  // Load token from localStorage if not provided in state
  useEffect(() => {
    if (!authToken) {
      const storedToken = localStorage.getItem("authToken") || localStorage.getItem("reg_token");
      if (storedToken) {
        setAuthToken(storedToken);
      } else {
        setFormError("Authentication token is missing. Please try signing up again.");
      }
    }
  }, [authToken]);

  const nextStep = () => setStep((prev) => prev + 1);
  const prevStep = () => setStep((prev) => prev - 1);

  const options = ["UI/UX", "Web Design", "Product", "Branding", "Research", "Graphics"];

  const toggleSelect = (item) => {
    if (hobbies.includes(item)) {
      setHobbies(hobbies.filter((tag) => tag !== item));
    } else {
      setHobbies([...hobbies, item]);
    }
  };

  const validateForm = () => {
    if (step === 1 && !city) {
      setFormError("Please enter your city");
      return false;
    }
    if (step === 2 && !institution) {
      setFormError("Please enter your institution");
      return false;
    }
    if (step === 2 && !qualification) {
      setFormError("Please select your qualification");
      return false;
    }
    if (step === 3 && !course) {
      setFormError("Please select your course of study");
      return false;
    }
    if (step === 3 && !yearOfStudy) {
      setFormError("Please select your year of study");
      return false;
    }
    setFormError("");
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    if (!authToken) {
      setFormError("Authentication token is missing. Please try again.");
      return;
    }

    const payload = {
      temp_token: authToken,
      roles: [role],
      city,
      year_of_study: yearOfStudy,
      course,
      hobbies,
      qualification,
      institution,
    };

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/complete-registration/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        if (data.token?.access) {
          localStorage.setItem("authToken", data.token.access);
          localStorage.removeItem("reg_token");
        }

        if (roles.length > 0) {
          const nextRole = roles[0];
          navigate(`/sign${nextRole.replace("_", "")}`, {
            state: {
              token: data.token?.access || authToken,
              remainingRoles: roles.slice(1),
            },
          });
        } else {
          alert("Registration complete!");
          window.location.href = "http://127.0.0.1:8000/";
        }
      } else {
        setFormError(data.error || "Registration failed");
        alert(data.error || "Registration failed");
      }
    } catch (err) {
      console.error("Error submitting registration:", err);
      setFormError("Something went wrong. Please check your connection and try again.");
    }
  };

  const handleContinue = () => {
    if (!validateForm()) return;

    if (step < 3) {
      nextStep();
    } else {
      handleSubmit();
    }
  };

  return (
    <div className="d-flex vh-100 font-sans">
      <div className="w-25 bg-light p-4">
        <img className="h-4 mb-3" alt="Logo" src="/assets/logo2.jpg" width="100px" />
        <div className="progress-container">
          <div className={`progress-step ${step >= 1 ? "active" : ""}`}>
            <div className="circle"></div>
            <span>Choose Role</span>
          </div>
          <div className={`progress-step ${step >= 2 ? "active" : ""}`}>
            <div className="circle"></div>
            <span>Tell us about yourself</span>
          </div>
          <div className={`progress-step ${step >= 3 ? "active" : ""}`}>
            <div className="circle"></div>
            <span>Choose how you use the app</span>
          </div>
        </div>
        <p className="sign-text text-muted small mt-4">
          Already have an account?{" "}
          <Link to="/signin" className="signin-link">
            Login
          </Link>
        </p>
      </div>

      <div className="w-75 p-5">
        {formError && <div className="alert alert-danger mb-3">{formError}</div>}

        {step === 1 && (
          <>
            <h2 className="mb-3">Tell us about yourself</h2>
            <div className="mb-3">
              <label className="form-label">City</label>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="form-control"
                placeholder="City"
                required
              />
            </div>
            <p>What's your area of interest?</p>
            <div className="d-flex flex-wrap gap-2 mb-4">
              {options.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => toggleSelect(item)}
                  className={`btn btn-sm rounded-pill ${
                    hobbies.includes(item) ? "btn-success" : "btn-outline-success"
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>
            <button onClick={handleContinue} className="btn btn-success rounded-pill px-4">
              Continue
            </button>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="mb-4">Education Info</h2>
            <form onSubmit={(e) => { e.preventDefault(); handleContinue(); }}>
              <div className="mb-3">
                <label className="form-label">Name of Institution</label>
                <input
                  type="text"
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                  placeholder="Name of Institution"
                  className="form-control"
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Qualification</label>
                {["Diploma", "Degree", "Honors", "Masters", "Other"].map((q) => (
                  <div className="form-check mb-2" key={q}>
                    <input
                      type="radio"
                      name="qualification"
                      value={q}
                      checked={qualification === q}
                      onChange={(e) => setQualification(e.target.value)}
                      className="form-check-input"
                      id={q.toLowerCase()}
                      required
                    />
                    <label htmlFor={q.toLowerCase()} className="form-check-label">
                      {q}
                    </label>
                  </div>
                ))}
              </div>
              <div className="d-flex gap-2">
                <button
                  type="button"
                  onClick={prevStep}
                  className="btn btn-outline-secondary rounded-pill px-4"
                >
                  Back
                </button>
                <button
                  type="submit"
                  className="btn btn-success rounded-pill px-4"
                >
                  Continue
                </button>
              </div>
            </form>
          </>
        )}

        {step === 3 && (
          <>
            <h2 className="mb-4">More Details</h2>
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
              <div className="mb-3">
                <label className="form-label">Course of study</label>
                {["Industrial Engineering", "Mechanical Engineering", "Software Development"].map(
                  (c) => (
                    <div className="form-check mb-2" key={c}>
                      <input
                        type="radio"
                        name="course"
                        value={c}
                        checked={course === c}
                        onChange={(e) => setCourse(e.target.value)}
                        className="form-check-input"
                        id={c.toLowerCase().replace(/\s+/g, "_")}
                        required
                      />
                      <label
                        htmlFor={c.toLowerCase().replace(/\s+/g, "_")}
                        className="form-check-label"
                      >
                        {c}
                      </label>
                    </div>
                  )
                )}
              </div>

              <div className="mb-3">
                <label className="form-label">Year of study</label>
                {[1, 2, 3, 4].map((y) => (
                  <div className="form-check mb-2" key={y}>
                    <input
                      type="radio"
                      name="year"
                      value={y}
                      checked={yearOfStudy === y}
                      onChange={(e) => setYearOfStudy(parseInt(e.target.value))}
                      className="form-check-input"
                      id={`year_${y}`}
                      required
                    />
                    <label htmlFor={`year_${y}`} className="form-check-label">
                      {`${y}${y === 1 ? "st" : y === 2 ? "nd" : y === 3 ? "rd" : "th"} Year`}
                    </label>
                  </div>
                ))}
              </div>

              <div className="d-flex gap-2">
                <button
                  type="button"
                  onClick={prevStep}
                  className="btn btn-outline-secondary rounded-pill px-4"
                >
                  Back
                </button>
                <button type="submit" className="btn btn-success rounded-pill px-4">
                  Finish
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default MultiStepForm;

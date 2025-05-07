import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const MultiStepForm = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const [step, setStep] = useState(1);
  const nextStep = () => setStep((prev) => prev + 1);
  const prevStep = () => setStep((prev) => prev - 1);

  const { token, remainingRoles = [] } = location.state || {};
  const [roles, setRoles] = useState(remainingRoles);
  const [authToken, setAuthToken] = useState(token);
  const [formError, setFormError] = useState("");

  const [cellnumber, setCellNumber] = useState("");
  const [city, setCity] = useState("");
  const [hobbies, setHobbies] = useState([]);
  const [status, setStatus] = useState("");
  const [usage, setUsage] = useState([]);

  const options = [
    "UI/UX",
    "Web Design",
    "Product",
    "Branding",
    "Research",
    "Graphics",
  ];

  const toggleSelect = (item) => {
    setHobbies((prev) =>
      prev.includes(item)
        ? prev.filter((tag) => tag !== item)
        : [...prev, item]
    );
  };

  useEffect(() => {
    if (!authToken) {
      const storedToken =
        localStorage.getItem("authToken") ||
        localStorage.getItem("reg_token");
      if (storedToken) {
        setAuthToken(storedToken);
      } else {
        setFormError(
          "Authentication token is missing. Please try signing up again."
        );
      }
    }
  }, [authToken]);

  const validateForm = () => {
    if (!city || !cellnumber) {
      alert("Please complete all required fields.");
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    const payload = {
      temp_token: authToken,
      roles: [location.state?.role],
      city,
      cellnumber,
      usage,
      hobbies,
      status,
    };

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/auth/complete-registration/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

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
          window.location.href = "/";
        }
      } else {
        setFormError(data.error || "Registration failed");
        alert(data.error || "Registration failed");
      }
    } catch (err) {
      console.error("Error submitting registration:", err);
      setFormError(
        "Something went wrong. Please check your connection and try again."
      );
    }
  };

  const handleContinue = () => {
    if (!validateForm()) return;

    if (step < 2) {
      nextStep();
    } else {
      handleSubmit();
    }
  };

  return (
    <div className="d-flex vh-100 font-sans">
      <div className="w-25 bg-light p-4">
        <img src="/logo.png" alt="Logo" className="mb-4" />
        <div className="progress-container">
          <div className={`progress-step ${step >= 1 ? "active" : ""}`}>
            <div className="circle"></div>
            <span>Area of Interest</span>
          </div>
          <div className={`progress-step ${step === 2 ? "active" : ""}`}>
            <div className="circle"></div>
            <span>Details</span>
          </div>
        </div>
        <p className="mt-5 text-muted small">
          Already have an account?{" "}
          <span
            className="text-success"
            style={{ cursor: "pointer" }}
            onClick={() => navigate("/login")}
          >
            Login
          </span>
        </p>
      </div>

      <div className="w-75 p-5">
        {step === 1 && (
          <div>
            <h2 className="mb-3">Tell us about yourself</h2>
            <p>What’s your area of interest?</p>
            <div className="d-flex flex-wrap gap-2 mb-4">
              {options.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => toggleSelect(item)}
                  className={`btn btn-sm rounded-pill ${
                    hobbies.includes(item)
                      ? "btn-success"
                      : "btn-outline-success"
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>
            <button
              onClick={handleContinue}
              className="btn btn-success rounded-pill px-4 me-3"
            >
              Continue
            </button>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="mb-4">Tell us more</h2>
            <form>
              <div className="mb-3">
                <label htmlFor="city">City</label>
                <input
                  type="text"
                  id="city"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="form-control"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="cell">Cell Number</label>
                <input
                  type="text"
                  id="cell"
                  value={cellnumber}
                  onChange={(e) => setCellNumber(e.target.value)}
                  className="form-control"
                />
              </div>

              <div className="mb-3">
                <label className="form-label">What best describes you?</label>
                <div className="form-check">
                  <input
                    type="radio"
                    name="status"
                    value="Completed Matric"
                    checked={status === "Completed Matric"}
                    onChange={(e) => setStatus(e.target.value)}
                    className="form-check-input"
                    id="matric"
                  />
                  <label htmlFor="matric" className="form-check-label">
                    Completed Matric
                  </label>
                </div>
                <div className="form-check">
                  <input
                    type="radio"
                    name="status"
                    value="Unemployed Graduate"
                    checked={status === "Unemployed Graduate"}
                    onChange={(e) => setStatus(e.target.value)}
                    className="form-check-input"
                    id="graduate"
                  />
                  <label htmlFor="graduate" className="form-check-label">
                    Unemployed Graduate
                  </label>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label">How do you use the app?</label>
                {[
                  "Admin or Legal",
                  "Finance and Tax",
                  "Plumbing",
                  "Electrical",
                  "Construction",
                  "Other",
                ].map((item, i) => (
                  <div className="form-check mb-2" key={i}>
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id={`usage-${i}`}
                      checked={usage.includes(item)}
                      onChange={(e) =>
                        setUsage((prev) =>
                          e.target.checked
                            ? [...prev, item]
                            : prev.filter((u) => u !== item)
                        )
                      }
                    />
                    <label
                      htmlFor={`usage-${i}`}
                      className="form-check-label"
                    >
                      {item}
                    </label>
                  </div>
                ))}
              </div>

              <button
                type="button"
                onClick={prevStep}
                className="btn btn-outline-secondary rounded-pill px-4 me-3"
              >
                Back
              </button>
              <button
                type="button"
                onClick={handleContinue}
                className="btn btn-success rounded-pill px-4"
              >
                Finish
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiStepForm;

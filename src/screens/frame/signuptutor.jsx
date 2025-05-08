import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const MultiStepForm = () => {
  const [step, setStep] = useState(1);
  const nextStep = () => setStep((prev) => prev + 1);
  const prevStep = () => setStep((prev) => prev - 1);

  const navigate = useNavigate();
  const location = useLocation();

  const { token, remainingRoles = []} = location.state || {};
  const [roles, setRoles] = useState(remainingRoles);
  const [authToken, setAuthToken] = useState(token);
  const [formError, setFormError] = useState("");
  const [role, setRole] = useState("tutor");

  const [formData, setFormData] = useState({
    city: "",
    phoneNumber: "",
    hobbies: [],
    hourlyRate: "",
    place: "",
    cv: null,
  });

  const options = ["UI/UX", "Web Design", "Product", "Branding", "Research", "Graphics"];

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

  const toggleSelect = (item) => {
    setFormData((prev) => ({
      ...prev,
      hobbies: prev.hobbies.includes(item)
        ? prev.hobbies.filter((tag) => tag !== item)
        : [...prev.hobbies, item],
    }));
  };

  const validateForm = () => {
    const { city, phoneNumber, hourlyRate, place, cv } = formData;
    if (!city || !phoneNumber || !hourlyRate || !place || !cv) {
      alert("Please complete all required fields including your CV.");
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    const payload = new FormData();
    payload.append("temp_token", authToken);
    payload.append("city", formData.city);
    payload.append("phone_number", formData.phoneNumber);
    payload.append("hourly_rate", formData.hourlyRate);
    payload.append("roles", role);
    formData.hobbies.forEach((hobby) => payload.append("hobbies", hobby));
    payload.append("place", formData.place);
    payload.append("cv", formData.cv);

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/complete-registration/", {
        method: "POST",
        body: payload,
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
          navigate("/");
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

  return (
    <div className="d-flex vh-100 font-sans">
      <div className="w-25 bg-light p-4">
        <img className="h-4" alt="Logo" src="/assets/logo2.jpg" width="100px" />
        <div className="progress-container">
          {["Area of Interest", "About You", "App Usage", "Final Details"].map(
            (stepTitle, index) => {
              const isCompleted = step > index + 1;
              const isActive = step === index + 1;

              return (
                <div
                  key={index}
                  className={`progress-step ${isActive ? "active" : ""} ${isCompleted ? "completed" : ""}`}
                >
                  <div className="circle"></div>
                  <span>{stepTitle}</span>
                </div>
              );
            }
          )}
        </div>
        <p className="mt-5 text-muted small">
          Already have an account? <span className="text-success">Login</span>
        </p>
      </div>

      <div className="w-75 p-5">
        {step === 1 && (
          <>
            <h2 className="mb-3">What’s your area of interest?</h2>
            <div className="d-flex flex-wrap gap-2 mb-4">
              {options.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => toggleSelect(item)}
                  className={`btn btn-sm rounded-pill ${
                    formData.hobbies.includes(item) ? "btn-success" : "btn-outline-success"
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>
            <div className="mb-4">
              <label htmlFor="city">City</label>
              <input
                type="text"
                placeholder="City"
                className="form-control"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
              />
            </div>
            <div className="d-flex gap-2">
              <button onClick={nextStep} className="btn btn-success rounded-pill px-4">
                Continue
              </button>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="mb-4">Tell us about yourself</h2>
            <form>
              <textarea
                placeholder="Tell us more about yourself (optional)"
                className="form-control mb-4"
                rows="4"
              />
              <div className="d-flex gap-2">
                <button
                  onClick={prevStep}
                  className="btn btn-outline-secondary rounded-pill px-4"
                >
                  Back
                </button>
                <button
                  onClick={nextStep}
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
            <h2 className="mb-4">How do you use the app?</h2>
            {["Online", "In-person at my House", "In-person within 30km", "All of the above"].map(
              (option) => (
                <div key={option} className="form-check mb-2">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id={option}
                    value={option}
                    checked={formData.place === option}
                    onChange={(e) => setFormData({ ...formData, place: e.target.value })}
                  />
                  <label htmlFor={option} className="form-check-label">
                    {option}
                  </label>
                </div>
              )
            )}
            <div className="d-flex gap-2 mt-4">
              <button
                onClick={prevStep}
                className="btn btn-outline-secondary rounded-pill px-4"
              >
                Back
              </button>
              <button
                onClick={nextStep}
                className="btn btn-success rounded-pill px-4"
              >
                Continue
              </button>
            </div>
          </>
        )}

        {step === 4 && (
          <>
            <h2 className="mb-4">Final Details</h2>
            <form>
              <div className="mb-3">
                <label htmlFor="phone">Cell Number</label>
                <input
                  type="text"
                  placeholder="Enter your phone number"
                  className="form-control"
                  value={formData.phoneNumber}
                  onChange={(e) => setFormData({ ...formData, phoneNumber: e.target.value })}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="hour-rate">Hourly Rate (R)</label>
                <input
                  type="number"
                  placeholder="Enter your hourly rate"
                  className="form-control"
                  value={formData.hourlyRate}
                  onChange={(e) => setFormData({ ...formData, hourlyRate: e.target.value })}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="cv">Upload Your CV</label>
                <input
                  type="file"
                  className="form-control"
                  onChange={(e) => setFormData({ ...formData, cv: e.target.files[0] })}
                />
              </div>

              <div className="d-flex gap-2">
                <button
                  onClick={prevStep}
                  type="button"
                  className="btn btn-outline-secondary rounded-pill px-4"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={handleSubmit}
                  className="btn btn-success rounded-pill px-4"
                >
                  Submit
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

import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const MultiStepForm = () => {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();
  const location = useLocation();

  const { token, remainingRoles = [] } = location.state || {};
  const [roles, setRoles] = useState(remainingRoles);
  const [authToken, setAuthToken] = useState(token);
  const [formError, setFormError] = useState("");

  const nextStep = () => setStep((prev) => prev + 1);
  const prevStep = () => setStep((prev) => prev - 1);


  const [selected, setSelected] = useState([]);
  const [hobbies, setHobbies] = useState([]);
  const [role, setRole] = useState("hs student");
  const [formData, setFormData] = useState({
    schoolName: "",
    studyLevel: "",
    hobbies: [],
    city: "",
    subjects: [],
  });

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

  const interestOptions = [
    "UI/UX", "Web Design", "Product", "Branding", "Research", "Graphics"
  ];

  const toggleSelect = (item) => {
    if (hobbies.includes(item)) {
      setHobbies(hobbies.filter((tag) => tag !== item));
    } else {
      setHobbies([...hobbies, item]);
    }
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubjectToggle = (subject) => {
    setFormData((prev) => {
      const subjects = prev.subjects.includes(subject)
        ? prev.subjects.filter((s) => s !== subject)
        : [...prev.subjects, subject];
      return { ...prev, subjects };
    });
  };

  const validateForm = () => {
    if (!formData.schoolName || !formData.city || !formData.studyLevel) {
      setFormError("Please fill in all the fields.");
      return false;
    }
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
      city: formData.city,
      schoolName: formData.schoolName,
      subjects: formData.subjects,
      hobbies:formData.studyLevel,
      studyLevel: formData.studyLevel,
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

  return (
    <div className="d-flex vh-100 font-sans">
      <div className="w-25 bg-light p-4">
        <img src="/logo.png" alt="Logo" className="mb-4" width="100px" />
        <div className="progress-container">
          <div className={`progress-step ${step >= 1 ? "active" : ""}`}>
            <div className="circle"></div>
            <span>Choose Role</span>
          </div>
          <div className={`progress-step ${step >= 2 ? "active" : ""}`}>
            <div className="circle"></div>
            <span>Tell us about school</span>
          </div>
          <div className={`progress-step ${step === 3 ? "active" : ""}`}>
            <div className="circle"></div>
            <span>Choose Subjects</span>
          </div>
        </div>
        <p className="mt-5 text-muted small">
          Already have an account? <span className="text-success">Login</span>
        </p>
      </div>

      <div className="w-75 p-5">
        {step === 1 && (
          <div>
            <h2 className="mb-3">Tell us about yourself</h2>
            <p>What’s your area of interest?</p>
            <div className="d-flex flex-wrap gap-2 mb-4">
              {interestOptions.map((item) => (
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
            <button
              className="btn btn-success rounded-pill px-4"
              onClick={nextStep}
            >
              Continue
            </button>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="mb-3">Your School Info</h2>
            <div className="mb-3">
              <label className="form-label fw-bold">Name of your school</label>
              <small className="form-text text-muted">The full name and address</small>
              <input
                type="text"
                name="schoolName"
                placeholder="Enter your answer"
                className="form-control mt-1"
                value={formData.schoolName}
                onChange={handleInputChange}
              />
            </div>

            <div className="mb-3">
              <label className="form-label fw-bold">City</label>
              <input
                type="text"
                name="city"
                placeholder="Enter your city"
                className="form-control mt-1"
                value={formData.city}
                onChange={handleInputChange}
              />
            </div>

            <div className="mb-4">
              <label className="form-label fw-bold">Level of study</label>
              {["Grade 10", "Grade 11", "Grade 12", "Other"].map((grade) => (
                <div key={grade} className="form-check">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="studyLevel"
                    value={grade}
                    checked={formData.studyLevel === grade}
                    onChange={handleInputChange}
                    id={grade}
                  />
                  <label className="form-check-label" htmlFor={grade}>
                    {grade}
                  </label>
                </div>
              ))}
            </div>

            <button
              className="btn btn-secondary rounded-pill px-4 me-2"
              onClick={prevStep}
            >
              Back
            </button>
            <button
              className="btn btn-success rounded-pill px-4"
              onClick={nextStep}
            >
              Continue
            </button>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="mb-3">Your Subjects</h2>
            <label className="form-label fw-bold">Select your subjects</label>
            <div className="mb-4">
              {["Mathematics", "Mathematical literacy", "Physical science", "Accounting", "Business studies", "Other"].map((subject) => (
                <div key={subject} className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id={subject}
                    checked={formData.subjects.includes(subject)}
                    onChange={() => handleSubjectToggle(subject)}
                  />
                  <label className="form-check-label" htmlFor={subject}>
                    {subject}
                  </label>
                </div>
              ))}
            </div>

            <button
              className="btn btn-secondary rounded-pill px-4 me-2"
              onClick={prevStep}
            >
              Back
            </button>
            <button className="btn btn-success rounded-pill px-4" onClick={handleSubmit}>
              Submit
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiStepForm;

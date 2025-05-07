import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";

const MultiStepFormService = () => {
  const navigate = useNavigate();
  const location = useLocation();

// Get token and remaining roles from location state
  const { token, remainingRoles = [] } = location.state || {};
  const [roles, setRoles] = useState(remainingRoles);
  const [authToken, setAuthToken] = useState(token);
  const [formError, setFormError] = useState("");

  const [role, setRole] = useState("service provider");
  const { remainingServices = [] } = location.state || {};
  const [services, setServices] = useState(remainingServices);

  const [step, setStep] = useState(1);
  const nextStep = () => setStep((prev) => prev + 1);
  const prevStep = () => setStep((prev) => prev - 1);

  const options = [
    "UI/UX",
    "Web Design",
    "Product",
    "Branding",
    "Research",
    "Graphics",
  ];
  const [hobbies, setSelected] = useState([]);
  const toggleSelect = (item) => {
    if (hobbies.includes(item)) {
      setSelected(hobbies.filter((tag) => tag !== item));
    } else {
      setSelected([...hobbies, item]);
    }
  };

  const [formData, setFormData] = useState({
    company: "",
    about: "",
    city: "",
    usageType: "",
    sectors: [],
    hobbies: [],
    serviceNeeds: [],
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
  

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const toggleCheckbox = (field, value) => {
    setFormData((prev) => {
      const updated = prev[field].includes(value)
        ? prev[field].filter((v) => v !== value)
        : [...prev[field], value];
      return { ...prev, [field]: updated };
    });
  };

  

  const handleFinalSubmitAndContinue = async () => {
   
    if (!authToken) {
      setFormError("Authentication token is missing. Please try again.");
      return;
    }

    const payload = {
      temp_token: authToken,
      roles: [role],
      about: formData.about,
      city: formData.city,
      usageType: formData.usageType,
      sectors: formData.sectors,
      hobbies:formData.hobbies,
      serviceNeeds: formData.serviceNeeds,
      company: formData.company,
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
        <img className="h-4" alt="Logo" src="/assets/logo2.jpg" width="100px" />
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
            <button onClick={nextStep} className="btn btn-success rounded-pill px-4">
              Next
            </button>
          </div>
        )}

            {step === 2 && (
              <div>
                <h2 className="mb-4">Tell us about yourself</h2>
                <form className="mb-3">
                  <div className="mb-3">
                    <label htmlFor="company">Name of Company</label>
                    <input
                      type="text"
                      placeholder="Name of company"
                      className="form-control"
                      value={formData.company}
                      onChange={(e) => handleChange("company", e.target.value)}
                    />
                  </div>

                  <div className="mb-3">
                    <label htmlFor="about">About Product/Service</label>
                    <textarea
                      placeholder="More details"
                      className="form-control"
                      rows="4"
                      value={formData.about}
                      onChange={(e) => handleChange("about", e.target.value)}
                    ></textarea>
                  </div>

                  <div className="mb-3">
                    <label htmlFor="city">City</label>
                    <input
                      type="text"
                      placeholder="Enter your city"
                      className="form-control"
                      value={formData.city}
                      onChange={(e) => handleChange("city", e.target.value)}
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">How do you use the app?</label>
                    <div className="form-check">
                      <input
                        type="radio"
                        name="usage"
                        className="form-check-input"
                        id="personal"
                        checked={formData.usageType === "personal"}
                        onChange={() => handleChange("usageType", "personal")}
                      />
                      <label htmlFor="personal" className="form-check-label">
                        In personal or side project
                      </label>
                    </div>
                    <div className="form-check">
                      <input
                        type="radio"
                        name="usage"
                        className="form-check-input"
                        id="professional"
                        checked={formData.usageType === "professional"}
                        onChange={() => handleChange("usageType", "professional")}
                      />
                      <label htmlFor="professional" className="form-check-label">
                        In professional or company work
                      </label>
                    </div>
                  </div>

                  <button type="button" onClick={nextStep} className="btn btn-success rounded-pill px-4">
                    Next
                  </button>
                </form>
              </div>
            )}


        {step === 3 && (
          <div>
            <h2 className="mb-4">Choose how you use the app</h2>
            <form>
              <div className="mb-3">
                <label className="form-label">How do you use the app?</label>
                {[
                  "Education And Training",
                  "Health and Medicine",
                  "ICT",
                  "Engineering",
                  "Arts & Culture",
                  "Tradition & Culture",
                  "Other",
                ].map((item) => (
                  <div key={item} className="form-check mb-3">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id={item}
                      checked={formData.sectors.includes(item)}
                      onChange={() => toggleCheckbox("sectors", item)}
                    />
                    <label htmlFor={item} className="form-check-label">
                      {item}
                    </label>
                  </div>
                ))}
              </div>

              <div className="mb-3">
                <label className="form-label">What services do you need?</label>
                {[
                  "Incubation",
                  "Acceleration",
                  "Grand Funding",
                  "Investor Funding",
                  "Marketing and Sales",
                  "Other",
                ].map((item) => (
                  <div key={item} className="form-check mb-3">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id={item}
                      checked={formData.serviceNeeds.includes(item)}
                      onChange={() => toggleCheckbox("serviceNeeds", item)}
                    />
                    <label htmlFor={item} className="form-check-label">
                      {item}
                    </label>
                  </div>
                ))}
              </div>

              <button type="button" onClick={nextStep} className="btn btn-success rounded-pill px-4">
                Next
              </button>
            </form>
          </div>
        )}

        {step === 4 && (
          <div>
            <h2 className="mb-4">Almost There</h2>
            <p>Include experiences and roles that are close to your location</p>
            <ul className="list-unstyled">
              <li>• Product design</li>
              <li>• UX writing</li>
              <li>• Graphic design</li>
              <li>• Frontend engineering</li>
              <li>• Branding</li>
              <li>• Design research</li>
              <li>• User testing</li>
              <li>• Content marketing</li>
            </ul>
            <button onClick={handleFinalSubmitAndContinue} className="btn btn-success rounded-pill px-4 mt-3">
              Continue
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiStepFormService;

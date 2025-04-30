import React, { useState, useEffect } from "react";

const MultiStepForm = () => {
  const [step, setStep] = useState(1);
  const [tempToken, setTempToken] = useState("");
  const [city, setCity] = useState("");
  const [institution, setInstitution] = useState("");
  const [qualification, setQualification] = useState("");
  const [course, setCourse] = useState("");
  const [yearOfStudy, setYearOfStudy] = useState("");
  const [hobbies, setHobbies] = useState([]);
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [submissionError, setSubmissionError] = useState(null);

  const nextStep = () => setStep((prev) => prev + 1);
  
  const options = [
    "UI/UX", "Web Design", "Product", "Branding", "Research", "Graphics",
  ];

  // Extract token from URL on component mount
  useEffect(() => {
    console.log('Component mounted, full URL:', window.location.href);
    
    // Get token from URL
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    console.log('Token from URL params:', token);
    
    if (token) {
      console.log('Setting token:', token);
      setTempToken(token);
      
      // Store token in sessionStorage
      sessionStorage.setItem('temp_registration_token', token);
      
      // Clean up URL (optional)
      const url = new URL(window.location);
      url.searchParams.delete("token");
      window.history.replaceState({}, document.title, url.toString());
    } else {
      // Try to get from sessionStorage if not in URL
      const storedToken = sessionStorage.getItem('temp_registration_token');
      console.log('No token in URL, checking storage:', storedToken);
      if (storedToken) {
        setTempToken(storedToken);
      } else {
        console.warn('No token found in URL or storage');
        // Could show error message here or redirect
      }
    }
  }, []);

  // Toggle hobby selection
  const toggleSelect = (item) => {
    if (hobbies.includes(item)) {
      setHobbies(hobbies.filter((tag) => tag !== item));
    } else {
      setHobbies([...hobbies, item]);
    }
  };

  // Submit form data
  const handleSubmit = () => {
    // Check required fields
    if (!city || !institution || !qualification || !course || !yearOfStudy) {
      alert("Please fill all required fields");
      return;
    }
    
    // Use token from state or fallback to sessionStorage
    const tokenToUse = tempToken || sessionStorage.getItem('temp_registration_token');
    
    if (!tokenToUse) {
      alert("Missing registration token. Please try registering again.");
      return;
    }
    
    console.log('Submitting with token:', tokenToUse);
    setFormSubmitted(true);
    setSubmissionError(null);
    
    fetch("http://127.0.0.1:8000/auth/complete-registration/", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        temp_token: tokenToUse,
        role: "student",
        city,
        institution,
        qualification,
        course,
        year_of_study: yearOfStudy,
        hobbies: hobbies.join(", "),
      }),
    })
    .then((res) => {
      console.log('Response status:', res.status);
      return res.json();
    })
    .then((data) => {
      console.log("Registration completed:", data);
      if (data.message === "Profile completed successfully") {
        alert("Registration successful! You can now log in.");
        // Clear the temp token from storage
        sessionStorage.removeItem('temp_registration_token');
        // Redirect to login page
        window.location.href = '/login';
      } else {
        setSubmissionError(data.error || data.message || 'Unknown error');
        setFormSubmitted(false);
      }
    })
    .catch((err) => {
      console.error("Registration error:", err);
      setSubmissionError(err.message);
      setFormSubmitted(false);
    });
  };

  return (
    <div className="d-flex vh-100 font-sans">
      {/* Left sidebar */}
      <div className="w-25 bg-light p-4">
        <img className="h-4" alt="Logo" src="/assets/logo2.jpg" width="100px" />
        <div className="progress-container">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
            <div className="circle"></div>
            <span>Choose Role</span>
          </div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
            <div className="circle"></div>
            <span>Tell us about yourself</span>
          </div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
            <div className="circle"></div>
            <span>Choose how you use the app</span>
          </div>
        </div>
        <p className="sign-text text-muted small">
          Already have an account? <a href="/login" className="text-success">Login</a>
        </p>
      </div>

      {/* Main content */}
      <div className="w-75 p-5">
        {submissionError && (
          <div className="alert alert-danger mb-3">
            Error: {submissionError}
          </div>
        )}
        
        {/* Step 1 */}
        {step === 1 && (
          <div>
            <h2 className="mb-3">Tell us about yourself</h2>
            <p>What's your area of interest</p>
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
            <div className="mb-5">
              <label htmlFor="city">City</label>
              <input 
                type="text"
                id="city"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="City"
                className="form-control" 
                required
              />
            </div>
            <button
              onClick={nextStep}
              className="btn btn-success rounded-pill px-4"
              disabled={!city}
            >
              Continue
            </button>
          </div>
        )}

        {/* Step 2 */}
        {step === 2 && (
          <div>
            <h2 className="mb-4">Education Info</h2>
            <form className="mb-3" onSubmit={(e) => { e.preventDefault(); nextStep(); }}>
              <div className="mb-3">
                <input
                  type="text"
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                  placeholder="Name of Institution"
                  className="form-control"
                  required
                />
              </div>

              <label className="form-label">Qualification</label>
              {["Diploma", "Degree", "Honors", "Masters", "Other"].map((q) => (
                <div className="form-check mb-2" key={q}>
                  <input
                    type="radio"
                    name="qualification"
                    className="form-check-input"
                    id={q}
                    value={q}
                    checked={qualification === q}
                    onChange={(e) => setQualification(e.target.value)}
                    required
                  />
                  <label htmlFor={q} className="form-check-label">
                    {q}
                  </label>
                </div>
              ))}

              <button
                type="submit"
                className="btn btn-success rounded-pill px-4 mt-3"
                disabled={!institution || !qualification}
              >
                Continue
              </button>
            </form>
          </div>
        )}

        {/* Step 3 */}
        {step === 3 && (
          <div>
            <h2 className="mb-4">Final Details</h2>
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
              <label className="form-label">Course of study</label>
              {["Industrial Engineering", "Mechanical Engineering", "Software Development"].map((c) => (
                <div className="form-check mb-2" key={c}>
                  <input
                    type="radio"
                    name="course"
                    className="form-check-input"
                    id={c}
                    value={c}
                    checked={course === c}
                    onChange={(e) => setCourse(e.target.value)}
                    required
                  />
                  <label htmlFor={c} className="form-check-label">
                    {c}
                  </label>
                </div>
              ))}

              <label className="form-label mt-3">Year of study</label>
              {["1st Year", "2nd Year", "3rd Year"].map((y) => (
                <div className="form-check mb-2" key={y}>
                  <input
                    type="radio"
                    name="year"
                    className="form-check-input"
                    id={y}
                    value={y}
                    checked={yearOfStudy === y}
                    onChange={(e) => setYearOfStudy(e.target.value)}
                    required
                  />
                  <label htmlFor={y} className="form-check-label">
                    {y}
                  </label>
                </div>
              ))}

              <button
                type="submit"
                className="btn btn-success rounded-pill px-4 mt-4"
                disabled={!course || !yearOfStudy || formSubmitted}
              >
                {formSubmitted ? (
                  <span>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Submitting...
                  </span>
                ) : (
                  "Submit"
                )}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiStepForm;

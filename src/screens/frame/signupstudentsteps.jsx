import React, { useState, useEffect } from "react";

const MultiStepForm = () => {
  const [step, setStep] = useState(1);
  const nextStep = () => setStep((prev) => prev + 1);

  const [tempToken, setTempToken] = useState("");
  const [institution, setInstitution] = useState("");
  const [qualification, setQualification] = useState("");
  const [course, setCourse] = useState("");
  const [yearOfStudy, setYearOfStudy] = useState("");
  const [hobbies, setHobbies] = useState([]);

  const options = [
    "UI/UX",
    "Web Design",
    "Product",
    "Branding",
    "Research",
    "Graphics",
  ];

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (token) {
      setTempToken(token);
    }
  }, []);

  const toggleSelect = (item) => {
    if (hobbies.includes(item)) {
      setHobbies(hobbies.filter((tag) => tag !== item));
    } else {
      setHobbies([...hobbies, item]);
    }
  };

  const handleSubmit = () => {
    fetch("http://127.0.0.1:8000/auth/complete-registration/", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${tempToken}`,
      },
      body: JSON.stringify({
        temp_token: tempToken,
        
        institution,
        qualification,
        course,
        year_of_study: yearOfStudy,
        hobbies: hobbies.join(", "),
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Registration completed:", data);
        if (data.token) {
          alert("Registration successful!");
          // Redirect or store token
        } else {
          alert("Something went wrong.");
        }
      })
      .catch((err) => console.error(err));
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
        <p className="sign-text text-muted small">
          Already have an account? <span className="text-success">Login</span>
        </p>
      </div>

      <div className="w-75 p-5">
        {step === 1 && (
          <div>
            <h2 className="mb-3">Tell us about yourself</h2>
            <p>What’s your area of interest</p>
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
              <input type="text" placeholder="City" className="form-control" />
            </div>
            <button
              onClick={nextStep}
              className="btn btn-success rounded-pill px-4"
            >
              Continue
            </button>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="mb-4">Education Info</h2>
            <form className="mb-3">
              <div className="mb-3">
                <input
                  type="text"
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                  placeholder="Name of Institution"
                  className="form-control"
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
                  />
                  <label htmlFor={q} className="form-check-label">
                    {q}
                  </label>
                </div>
              ))}

              <button
                type="button"
                onClick={nextStep}
                className="btn btn-success rounded-pill px-4 mt-3"
              >
                Continue
              </button>
            </form>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="mb-4">Final Details</h2>
            <form>
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
                  />
                  <label htmlFor={y} className="form-check-label">
                    {y}
                  </label>
                </div>
              ))}

              <button
                type="button"
                onClick={handleSubmit}
                className="btn btn-success rounded-pill px-4 mt-4"
              >
                Submit
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiStepForm;

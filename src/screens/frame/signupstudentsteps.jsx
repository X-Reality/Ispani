import React, { useState } from "react";

const MultiStepForm = () => {
  const [step, setStep] = useState(1);
  const nextStep = () => setStep((prev) => prev + 1);
  const prevStep = () => setStep((prev) => prev - 1);
  const [tempToken, setTempToken] = useState("");
  const [username, setUsername] = useState("");
  const [institution, setInstitution] = useState("");
  const [qualification, setQualification] = useState("");
  const [course, setCourse] = useState("");
  const [yearOfStudy, setYearOfStudy] = useState("");
  const [hobbies, setHobbies] = useState([]);
  const [pieceJobs, setPieceJobs] = useState("");

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
    fetch("http://127.0.0.1:8000/complete-registration/", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        "Authorization": "Bearer $token",
      },
      body: JSON.stringify({
        temp_token: tempToken,
        username: username,
        institution: institution,
        qualification: qualification,
        course: course,
        year_of_study: yearOfStudy,
        hobbies: hobbies.join(", "),
        piece_jobs: pieceJobs,
        communication_preference: "email",
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Registration completed:", data);
        if (data.token) {
          alert("Registration successful!");
          // Optionally redirect or store token
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
        <div class="progress-container">
          <div class="progress-step active">
            <div class="circle"></div>
            <span>Choose Role</span>
          </div>
          <div class="progress-step">
            <div class="circle"></div>
            <span>Tell us about yourself</span>
          </div>
          <div class="progress-step">
            <div class="circle"></div>
            <span>Choose how you use the app</span>
          </div>
        </div>
        <p className=" sign-text text-muted small">
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
                    selected.includes(item)
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
            <h2 className="mb-4">Tell us about yourself</h2>
            <form className="mb-3">
              <div className="mb-3">
                <input
                  type="text"
                  placeholder="Name of Institution"
                  className="form-control"
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Qualification</label>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="personal"
                  />
                  <label htmlFor="personal" className="form-check-label">
                    Diploma
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="professional"
                  />
                  <label htmlFor="professional" className="form-check-label">
                    Degree
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="professional"
                  />
                  <label htmlFor="professional" className="form-check-label">
                    Honors
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="professional"
                  />
                  <label htmlFor="professional" className="form-check-label">
                    Masters
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="professional"
                  />
                  <label htmlFor="professional" className="form-check-label">
                    Other
                  </label>
                </div>
              </div>

              <button
                type="button"
                onClick={nextStep}
                className="btn btn-success rounded-pill px-4"
              >
                Continue
              </button>
            </form>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="mb-4">Tell us More</h2>
            <form>
              <div className="mb-3">
                <label className="form-label">Course of study</label>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="personal"
                  />
                  <label htmlFor="personal" className="form-check-label">
                    Industrial Engineering
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="professional"
                  />
                  <label htmlFor="professional" className="form-check-label">
                    Mechincal Enginnering
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    className="form-check-input"
                    id="student"
                  />
                  <label htmlFor="student" className="form-check-label">
                    Software Development
                  </label>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label">Year of study</label>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="personal"
                  />
                  <label htmlFor="personal" className="form-check-label">
                    1st Year
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="professional"
                  />
                  <label htmlFor="professional" className="form-check-label">
                    2nd Year
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="radio"
                    className="form-check-input"
                    id="student"
                  />
                  <label htmlFor="student" className="form-check-label">
                    3rd year
                  </label>
                </div>
              </div>

              <button
                type="button"
                onClick={nextStep}
                className="btn btn-success rounded-pill px-4"
              >
                Continue
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiStepForm;

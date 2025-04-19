import React, { useState } from "react";

const MultiStepForm = () => {
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

  const [selected, setSelected] = useState([]);

  const toggleSelect = (item) => {
    if (selected.includes(item)) {
      setSelected(selected.filter((tag) => tag !== item));
    } else {
      setSelected([...selected, item]);
    }
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
              <div class="progress-step">
                <div class="circle"></div>
                <span>Create An Account</span>
              </div>
              <div class="progress-step">
                <div class="circle"></div>
                <span>Create An Account</span>
              </div>
              <div class="progress-step">
                <div class="circle"></div>
                <span>Create An Account</span>
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
                  placeholder="Your Address"
                  className="form-control"
                />
              </div>
              <div className="mb-3">
                <textarea
                  placeholder="About you"
                  className="form-control"
                  rows="4"
                ></textarea>
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
                <label className="form-label">How do you use the app?</label>
                <div className="form-check mb-3">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="student"
                  />
                  <label htmlFor="student" className="form-check-label">
                    Mathematics
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="student"
                  />
                  <label htmlFor="student" className="form-check-label">
                    Physicla Science
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="student"
                  />
                  <label htmlFor="student" className="form-check-label">
                    Accounting
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="student"
                  />
                  <label htmlFor="student" className="form-check-label">
                    Astronomy
                  </label>
                </div>
                <div className="form-check mb-3">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="student"
                  />
                  <label htmlFor="student" className="form-check-label"></label>
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
        {step === 4 && (
          <div>
            <h2 className="mb-4">Tell us about yourself</h2>
            <form className="mb-3">
              <div className="mb-3">
                <label htmlFor="About "> Cell Number </label>
                <input
                  type="text"
                  placeholder="Name of company"
                  className="form-control"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="About ">Hour Rate</label>
                <input
                  type="text"
                  placeholder="Name of company"
                  className="form-control"
                />
              </div>

              <div className="mb-3">
                <label className="form-label">
                  Preferred place of Tutoring
                </label>
                <div className="form-check">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="personal"
                  />
                  <label htmlFor="personal" className="form-check-label">
                    Online
                  </label>
                </div>
                <div className="form-check">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="professional"
                  />
                  <label htmlFor="professional" className="form-check-label">
                    In-person at my House{" "}
                  </label>
                </div>
                <div className="form-check">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="professional"
                  />
                  <label htmlFor="professional" className="form-check-label">
                    in person within 30km
                  </label>
                </div>
                <div className="form-check">
                  <input
                    type="radio"
                    name="usage"
                    className="form-check-input"
                    id="professional"
                  />
                  <label htmlFor="professional" className="form-check-label">
                    all of the above
                  </label>
                </div>
              </div>
              <div className="mb-3">
                <label htmlFor="About ">Hour Rate</label>
                <input
                  type="file"
                  placeholder="Name of company"
                  className="form-control"
                />
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

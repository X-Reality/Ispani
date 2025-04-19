import React, { useState } from "react";


const MultiStepFormService = () => {
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
        </div>
        <p className="mt-5 text-muted small">Already have an account? <span className="text-success">Login</span></p>
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
            selected.includes(item) ? "btn-success" : "btn-outline-success"
          }`}
        >
          {item}
        </button>
      ))}
    </div>
            <button onClick={nextStep} className="btn btn-success rounded-pill px-4">Next</button>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="mb-4">Tell us about yourself</h2>
            <form className="mb-3">
              <div className="mb-3">
              <label htmlFor="About ">Name of Company</label>
                <input type="text" placeholder="Name of company" className="form-control" />
              </div>
        
              <div className="mb-3">
                <label htmlFor="About ">About Product/Service</label>
                <textarea placeholder="More details" className="form-control" rows="4"></textarea>
              </div>
       
              <div className="mb-3">
                <label className="form-label">How do you use the app?</label>
                <div className="form-check">
                  <input type="radio" name="usage" className="form-check-input" id="personal" />
                  <label htmlFor="personal" className="form-check-label">In personal or side project</label>
                </div>
                <div className="form-check">
                  <input type="radio" name="usage" className="form-check-input" id="professional" />
                  <label htmlFor="professional" className="form-check-label">In professional or company work</label>
                </div>
              </div>
             
              <button type="button" onClick={nextStep} className="btn btn-success rounded-pill px-4">Next</button>
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
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Education And Training </label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Health and Medicine</label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">ICT</label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Engineering</label>
              </div> 
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Arts & Culture</label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Tradition & Culture</label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Other</label>
              </div>
            
              
              </div>
              <div className="mb-3">
                <label className="form-label">How do you use the app?</label>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Incubation</label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Acceleration</label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Grand Funding</label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Investor Funding</label>
              </div> 
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Marketing and Sales</label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Marketing and Sales</label>
              </div>
              <div className="form-check mb-3">
                <input type="checkbox" className="form-check-input" id="student" />
                <label htmlFor="student" className="form-check-label">Other</label>
              </div>

              </div>
              <button type="button" onClick={nextStep} className="btn btn-success rounded-pill px-4">Next</button>
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
            <button onClick={nextStep} className="btn btn-success rounded-pill px-4 mt-3">Next</button>
          </div>
        )}

        
      </div>
    </div>
  );
};

export default MultiStepFormService;

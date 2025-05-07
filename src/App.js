import "./App.css";
import "./screens/frame/frame";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { Frame } from "./screens/frame/frame";
import Signup from "./screens/frame/signup";
import Signin from "./screens/frame/signin";
import VerifyOtp from "./screens/frame/otp";
import Roles from "./screens/frame/roles";
import MultiStepForm from "./screens/frame/signupstudentsteps";
import MultiStepFormService from "./screens/frame/signupservicesproviderstep";
import LearnerForm from "./screens/frame/signuphstudent";
import TutorForm from "./screens/frame/signuptutor";
import JobSeekerForm from "./screens/frame/signupjobsekker";

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<Signup />} />
          <Route path="/signin" element={<Signin />} /> 
          <Route path="/otp" element={<VerifyOtp />} />
          <Route path="/roles" element={<Roles />} />
          <Route path="/signupstudent" element={<MultiStepForm />} />
          <Route path="/signservice" element={<MultiStepFormService />} />
          <Route path="/signlearner" element={<LearnerForm />} />
          <Route path="/signjobseeker" element={<JobSeekerForm />} />
          <Route path="/signtutor" element={<TutorForm />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;

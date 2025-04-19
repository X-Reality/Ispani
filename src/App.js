import "./App.css";
import "./screens/frame/frame";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { Frame } from "./screens/frame/frame";
import Signup from "./screens/frame/signup";
import Roles from "./screens/frame/roles";
import MultiStepForm from "./screens/frame/signupstudentsteps";
import MultiStepFormService from "./screens/frame/signupservicesproviderstep";

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<Signup />} />
          <Route path="/roles" element={<Roles />} />
          <Route path="/signupstudent" element={<MultiStepForm />} />
          <Route path="/signservice" element={<MultiStepFormService />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;

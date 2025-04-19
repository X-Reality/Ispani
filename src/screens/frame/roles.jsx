import React from "react";
import { Input } from "../../components/ui/input";
import { Button } from "../../components/ui/button";

const Roles = () => {
  return (
    <div className="role">
      <div className="container">
        <header className="d-flex justify-content-between align-items-center mt-2">
        <img className="h-4" alt="Logo" src="/assets/logo2.jpg" width="100px" />
          <Button variant="outline" className="btn btn-dark">
            <span className="font-weight-semibold text-white">Download</span>
          </Button>
        </header>
        <div className="row ">
          <div className="col-md-6">
            <div className="box"></div>
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
          </div>
          <div className="col-md-6">
            <h4>
              Lorem ipsum dolor sit amet consectetur adipisicing elit. Totam
              distinctio numquam eum.
            </h4>
            <div className="row">
              <div className="col-md-6">
                <div className="card">
                  <div className="card-body">
                    <i className="bx bx-user-circle"></i>
                    <h6>Student</h6>
                  </div>
                </div>
              </div>
              <div className="col-md-6">
                <div className="card">
                  <div className="card-body">
                    <i className="bx bx-user-circle"></i>
                    <h6>Tutor</h6>
                  </div>
                </div>
              </div>
              <div className="col-md-6">
                <div className="card">
                  <div className="card-body">
                    <i className="bx bx-user-circle"></i>
                    <h6> HS Student</h6>
                  </div>
                </div>
              </div>
              <div className="col-md-6">
                <div className="card">
                  <div className="card-body">
                    <i class="bx bx-briefcase"></i>
                    <h6>Service Provider</h6>
                  </div>
                </div>
              </div>
              <div className="col-md-6">
                <div className="card">
                  <div className="card-body">
                    <i class="bx bx-briefcase"></i>
                    <h6>Job Seeker</h6>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Roles;

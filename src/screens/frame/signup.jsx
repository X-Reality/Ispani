import React from "react";
import { Input } from "../../components/ui/input";
import { Button } from "../../components/ui/button";

const Signup = () => {
  return (
    <div className="sign">
      <div className="container">
        <header className="d-flex justify-content-between align-items-center mt-2">
          <img className="h-4" alt="Logo" src="/assets/logo2.jpg" width="100px" />
          <Button variant="outline" className="btn btn-dark">
            <span className="font-weight-semibold text-white">Download</span>
          </Button>
        </header>
        <div className="row mt-5">
          <div className="col-md-6">
            <h2>Create an Account</h2>
            <p>Lorem ipsum dolor sit, amet consectetur adipisicing elit.</p>
            <form action="" method="get">
              <div className="mb-3">
                <label for="Name" class="form-label">
                  Name
                </label>
                <Input id="Name" name="Name" placeholder="Please add Name" />
              </div>
              <div className="mb-3">
                <label For="Name">Email</label>
                <Input
                  type="email"
                  id=""
                  name=""
                  placeholder="Please add Name"
                />
              </div>
              <div className="mb-3">
                <label htmlFor="Name">Password</label>
                <Input
                  type="password"
                  id=""
                  name=""
                  placeholder="Please add Name"
                />
              </div>
              <div class="form-check mb-3">
                <input
                  className="form-check-input"
                  type="checkbox"
                  value=""
                  id="invalidCheck"
                  required
                />
                <label className="form-check-label" for="invalidCheck">
                  Agree to terms and conditions
                </label>
                <div className="invalid-feedback">
                  You must agree before submitting.
                </div>
              </div>
              <div className="mb-3">
                <Button variant="outline" className="  btn btn-dark">
                  <span className=" font-weight-semibold text-white">
                    Sign Up
                  </span>
                </Button>
              </div>
            </form>
            <div className="or mt-4 mb-4 ">
              <span>OR</span>
            </div>
            <Button variant="outline" className="  btn btn-outline-dark mb-3">
              <span className=" font-weight-semibold ">
                Sign Up with google.com
              </span>
            </Button>
            <Button variant="outline" className="  btn btn-outline-dark mb-5">
              <span className=" font-weight-semibold ">
                Sign Up with linked.com
              </span>
            </Button>
            <h6>
              Already have an account{" "}
              <span className="signin-link">Sign in</span>
            </h6>
          </div>
          <div className="col-md-6">
            <div className="box"></div>
            <img
              className="h-4"
              alt="Logo"
              src="/assets/Spaniprototypemockup1.png"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;

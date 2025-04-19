import React from "react";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Card, CardContent } from "../../components/ui/card";
import { Checkbox } from "../../components/ui/checkbox";
import { Input } from "../../components/ui/input";
import { Separator } from "../../components/ui/separator";

export const Frame = () => {
  const steps = [
    { id: 1, title: "Choose Role", completed: true },
    { id: 2, title: "Tell us about yourself", completed: true, active: true },
    { id: 3, title: "Choose how you use the app", completed: false },
    { id: 4, title: "Create An Account", completed: false },
    { id: 5, title: "Create An Account", completed: false },
    { id: 6, title: "Create An Account", completed: false },
  ];

  const interestAreas = [
    { id: 1, name: "Chess" },
    { id: 2, name: "Soccer" },
    { id: 3, name: "Rugby" },
    { id: 4, name: "Singing and Choir" },
    { id: 5, name: "Entrepreneurship" },
    { id: 6, name: "Sports" },
    { id: 7, name: "Spirituality" },
  ];

  return (
    <div className="bg-transparent d-flex justify-content-center w-100">
      <div className="w-100" style={{ maxWidth: "80rem" }}>
        <div className="w-100 bg-white overflow-hidden p-4">
          {/* Header */}
          <header className="d-flex justify-content-between align-items-center mb-5">
            <img className="h-4" alt="Logo" src="/rectangle-103-9.png" />
            <Button variant="outline" className="btn btn-dark">
              <span className="font-weight-semibold text-white">Download</span>
            </Button>
          </header>

          {/* Main Section */}
          <main className="mt-4">
            <div className="text-center mb-5">
              <h1 className="h3 h-md4 font-weight-bold text-dark mb-4">
                Tell us about yourself
              </h1>
              <p className="lead text-muted max-w-2xl mx-auto">
                dsfhndsfdfds nd sf sdf sdf nsd j sdf
                <br />
                jdf sjkddf sdjdsf
              </p>
            </div>

            {/* Steps */}
            <div className="d-flex flex-column flex-md-row gap-3 mb-5">
              <div className="d-flex flex-column gap-3">
                {steps.map((step, index) => (
                  <div
                    key={step.id}
                    className="d-flex align-items-center gap-3"
                  >
                    <div
                      className={`w-3 h-3 rounded-circle border-2 d-flex align-items-center justify-content-center ${
                        step.active
                          ? "bg-success border-success"
                          : "bg-white border-success"
                      }`}
                    />
                    <span
                      className={`h6 ${
                        step.active ? "font-weight-normal" : "font-weight-light"
                      }`}
                    >
                      {step.title}
                    </span>
                    {index < steps.length - 1 && (
                      <div className="w-1 h-5 bg-light ml-3" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Interests */}
            <div className="mb-5">
              <h2 className="h4 font-weight-normal mb-4">
                What's your area of interest
              </h2>

              <div className="d-flex flex-wrap gap-3">
                {interestAreas.map((interest) => (
                  <Badge
                    key={interest.id}
                    variant="outline"
                    className="px-4 py-2 h5 bg-secondary rounded-pill"
                  >
                    {interest.name}
                  </Badge>
                ))}
              </div>

              <div className="mt-4">
                <div className="d-flex align-items-center gap-2">
                  <span className="h5">Other</span>
                  <Separator className="flex-1 h-1 bg-success" />
                </div>
              </div>

              {/* Card with Input + Checkboxes */}
              <Card className="mt-4">
                <CardContent className="p-4 d-flex flex-column gap-3">
                  <h3 className="h5 font-weight-semibold mb-2">
                    Customize your interests
                  </h3>

                  <div className="d-flex flex-column flex-md-row gap-3 align-items-center">
                    <Input placeholder="Add a custom interest..." />
                    <Button className="bg-success text-white">Add</Button>
                  </div>

                  <div className="mt-3">
                    <div className="d-flex flex-column gap-2"></div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Next Button */}
            <Button className="btn btn-success">Next</Button>
          </main>

          {/* Footer */}
          <footer className="mt-5 d-flex align-items-center justify-content-center gap-2">
            <span className="h6">Already have an account?</span>
            <Button variant="link" className="text-success h6 p-0">
              Sign In
            </Button>
          </footer>
        </div>
      </div>
    </div>
  );
};

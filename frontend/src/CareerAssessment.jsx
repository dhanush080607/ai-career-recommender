import { useState } from "react";
import "./CareerAssessment.css";

const API_URL = "http://127.0.0.1:5000";

function CareerAssessment({
  token,
  onSessionExpired,
  onComplete,
}) {
  const [formData, setFormData] = useState({
    fullName: "",
    education: "",
    skills: [],
    interests: [],
    proficiency: "",
    careerGoal: "",
  });

  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [assessmentId, setAssessmentId] = useState(null);

  const skillOptions = [
    "Python",
    "Java",
    "C++",
    "SQL",
    "HTML & CSS",
    "JavaScript",
    "Machine Learning",
    "Data Analysis",
  ];

  const interestOptions = [
    "Artificial Intelligence",
    "Data Science",
    "Web Development",
    "Cybersecurity",
    "Cloud Computing",
    "Software Development",
  ];

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    setErrorMessage("");
  }

  function handleCheckboxChange(event, field) {
    const { value, checked } = event.target;

    setFormData((previous) => ({
      ...previous,
      [field]: checked
        ? [...previous[field], value]
        : previous[field].filter((item) => item !== value),
    }));

    setErrorMessage("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!token) {
      setErrorMessage("Please log in before submitting your assessment.");
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
      const response = await fetch(`${API_URL}/api/recommendations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          top_n: 3,
        }),
      });

      const result = await response.json();

      if (response.status === 401) {
        onSessionExpired?.();
        return;
      }

      if (!response.ok) {
        throw new Error(
          result.error || "Unable to generate career recommendations."
        );
      }

      setAssessmentId(result.assessmentId);
      setSubmitted(true);
    } catch (error) {
      setErrorMessage(
        error.message === "Failed to fetch"
          ? "Cannot connect to the backend. Please check that Flask is running."
          : error.message
      );
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <div className="assessment-page">
        <div className="assessment-container">
          <div className="assessment-success">
            <div className="success-icon">✓</div>

            <h2>Recommendations Ready!</h2>

            <p>
              Thank you, {formData.fullName}! Your assessment has
              been analyzed and the best-fit careers are ready.
            </p>

            <p>
              <strong>Assessment ID:</strong> {assessmentId}
            </p>

            <p className="success-note">
              You can return to your dashboard to review your recommendations,
              skill gaps, and roadmap guidance.
            </p>

            <button
              className="assessment-button"
              onClick={() => onComplete?.()}
            >
              Return to My Dashboard →
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="assessment-page">
      <div className="assessment-container">
        <div className="assessment-heading">
          <span className="assessment-badge">
            ✦ AI CAREER ASSESSMENT
          </span>

          <h1>
            Let's Discover Your <span>Career Path</span>
          </h1>

          <p>
            Tell us about your skills, education, and interests.
            We'll use this information to help identify suitable careers.
          </p>
        </div>

        <form className="assessment-form" onSubmit={handleSubmit}>
          <div className="form-section">
            <div className="form-section-heading">
              <span>01</span>
              <div>
                <h2>Personal Information</h2>
                <p>Let's start with the basics.</p>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="fullName">Full Name</label>

              <input
                id="fullName"
                name="fullName"
                type="text"
                placeholder="Enter your full name"
                value={formData.fullName}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="education">Current Education</label>

              <select
                id="education"
                name="education"
                value={formData.education}
                onChange={handleChange}
                required
              >
                <option value="">Select your education</option>
                <option value="Diploma">Diploma</option>
                <option value="BTech">B.Tech / B.E.</option>
                <option value="BSc">B.Sc.</option>
                <option value="BCA">BCA</option>
                <option value="MTech">M.Tech / M.E.</option>
                <option value="MSc">M.Sc.</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-heading">
              <span>02</span>
              <div>
                <h2>Your Technical Skills</h2>
                <p>Select all skills you currently know.</p>
              </div>
            </div>

            <div className="options-grid">
              {skillOptions.map((skill) => (
                <label className="option-card" key={skill}>
                  <input
                    type="checkbox"
                    value={skill}
                    checked={formData.skills.includes(skill)}
                    onChange={(event) =>
                      handleCheckboxChange(event, "skills")
                    }
                  />
                  <span>{skill}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-heading">
              <span>03</span>
              <div>
                <h2>Your Interests</h2>
                <p>Choose the fields that interest you most.</p>
              </div>
            </div>

            <div className="options-grid">
              {interestOptions.map((interest) => (
                <label className="option-card" key={interest}>
                  <input
                    type="checkbox"
                    value={interest}
                    checked={formData.interests.includes(interest)}
                    onChange={(event) =>
                      handleCheckboxChange(event, "interests")
                    }
                  />
                  <span>{interest}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-heading">
              <span>04</span>
              <div>
                <h2>Skill Proficiency</h2>
                <p>How would you describe your current level?</p>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="proficiency">Your Level</label>

              <select
                id="proficiency"
                name="proficiency"
                value={formData.proficiency}
                onChange={handleChange}
                required
              >
                <option value="">Select your skill level</option>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-heading">
              <span>05</span>
              <div>
                <h2>Career Goals</h2>
                <p>Tell us what you want to achieve.</p>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="careerGoal">
                What is your career goal?
              </label>

              <textarea
                id="careerGoal"
                name="careerGoal"
                placeholder="Example: I want to become a Data Scientist and work on AI projects."
                rows="4"
                value={formData.careerGoal}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          {errorMessage && (
            <div className="assessment-error" role="alert">
              {errorMessage}
            </div>
          )}

          <button
            type="submit"
            className="assessment-button"
            disabled={loading}
          >
            {loading ? "Saving Assessment..." : "Submit Assessment"}
            {!loading && <span> →</span>}
          </button>

          <p className="privacy-note">
            Your assessment is associated with your account and can
            be retrieved from your personal dashboard.
          </p>
        </form>
      </div>
    </div>
  );
}

export default CareerAssessment;

import { useState } from "react";
import { Eye, EyeOff, Mail, Lock, UserRound, GraduationCap } from "lucide-react";
import "./auth.css";

const API_URL = "http://127.0.0.1:5000/api";

export default function Auth({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    education: "",
  });

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    setError("");
    setSuccess("");
  }

  function switchMode() {
    setIsRegister((previous) => !previous);
    setError("");
    setSuccess("");
    setShowPassword(false);
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    const email = formData.email.trim().toLowerCase();
    const password = formData.password;

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    if (isRegister && !formData.fullName.trim()) {
      setError("Please enter your full name.");
      return;
    }

    if (isRegister && password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    if (isRegister && !formData.education.trim()) {
      setError("Please enter your education details.");
      return;
    }

    const endpoint = isRegister ? "/auth/register" : "/auth/login";

    const requestBody = isRegister
      ? {
          fullName: formData.fullName.trim(),
          name: formData.fullName.trim(),
          email,
          password,
          education: formData.education.trim(),
        }
      : {
          email,
          password,
        };

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          result.message ||
            result.error ||
            result.msg ||
            (response.status === 404
              ? "Authentication endpoint not found. Please check your backend API routes."
              : response.status === 401
                ? "Invalid email or password."
                : "Authentication failed. Please try again.")
        );
      }

      if (isRegister) {
        setSuccess("Account created successfully! You can now sign in.");
        setIsRegister(false);

        setFormData((previous) => ({
          ...previous,
          fullName: "",
          password: "",
          education: "",
        }));

        return;
      }

      const token =
        result.token ||
        result.accessToken ||
        result.access_token;

      const user = result.user || result.profile;

      if (!token) {
        throw new Error(
          "Login succeeded, but the backend did not return a token. Check the login API response."
        );
      }

      if (typeof onLogin !== "function") {
        throw new Error(
          "Login handler is missing. Please check the onLogin prop in App.jsx."
        );
      }

      onLogin({
        token,
        user: user || { email },
      });
    } catch (err) {
      if (
        err instanceof TypeError &&
        err.message.toLowerCase().includes("fetch")
      ) {
        setError(
          "Cannot connect to the backend. Please start your Flask server and try again."
        );
      } else {
        setError(err.message || "Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <GraduationCap size={32} />
          </div>

          <h1>AI Career Navigator</h1>

          <p>
            {isRegister
              ? "Create your account and start your career journey."
              : "Welcome back! Continue your career journey."}
          </p>
        </div>

        <div className="auth-tabs">
          <button
            type="button"
            className={!isRegister ? "active" : ""}
            onClick={() => {
              setIsRegister(false);
              setError("");
              setSuccess("");
            }}
          >
            Sign In
          </button>

          <button
            type="button"
            className={isRegister ? "active" : ""}
            onClick={() => {
              setIsRegister(true);
              setError("");
              setSuccess("");
            }}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div className="auth-message auth-error" role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className="auth-message auth-success" role="status">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {isRegister && (
            <>
              <label htmlFor="fullName">Full Name</label>

              <div className="auth-input-wrapper">
                <UserRound size={19} />

                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  placeholder="Enter your full name"
                  value={formData.fullName}
                  onChange={handleChange}
                  autoComplete="name"
                  required
                />
              </div>

              <label htmlFor="education">Education</label>

              <div className="auth-input-wrapper">
                <GraduationCap size={19} />

                <input
                  id="education"
                  name="education"
                  type="text"
                  placeholder="e.g. B.Tech - Data Science"
                  value={formData.education}
                  onChange={handleChange}
                  autoComplete="organization-title"
                  required
                />
              </div>
            </>
          )}

          <label htmlFor="email">Email Address</label>

          <div className="auth-input-wrapper">
            <Mail size={19} />

            <input
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              autoComplete="email"
              required
            />
          </div>

          <label htmlFor="password">Password</label>

          <div className="auth-input-wrapper">
            <Lock size={19} />

            <input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              autoComplete={
                isRegister ? "new-password" : "current-password"
              }
              minLength={isRegister ? 6 : undefined}
              required
            />

            <button
              type="button"
              className="auth-password-toggle"
              onClick={() => setShowPassword((previous) => !previous)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
            </button>
          </div>

          <button
            type="submit"
            className="auth-submit-btn"
            disabled={loading}
          >
            {loading
              ? "Please wait..."
              : isRegister
                ? "Create Account"
                : "Sign In"}
          </button>
        </form>

        <p className="auth-switch-text">
          {isRegister
            ? "Already have an account?"
            : "New to AI Career Navigator?"}{" "}

          <button type="button" onClick={switchMode}>
            {isRegister ? "Sign in" : "Create an account"}
          </button>
        </p>

        <p className="auth-footer">
          Discover your strengths. Build your future.
        </p>
      </div>
    </div>
  );
}

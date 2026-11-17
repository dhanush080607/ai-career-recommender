import { useEffect, useState } from "react";
import "./App.css";
import CareerAssessment from "./CareerAssessment";
import Auth from "./Auth";
import Dashboard from "./Dashboard";

const CURRENT_YEAR = new Date().getFullYear();
const API_URL = "http://127.0.0.1:5000";

function App() {
  const [page, setPage] = useState("home");
  const [session, setSession] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);

  const careers = [
    {
      icon: "📊",
      title: "Data Scientist",
      description:
        "Analyze complex data and build predictive machine learning models.",
      skills: ["Python", "Statistics", "Machine Learning"],
    },
    {
      icon: "🤖",
      title: "AI Engineer",
      description:
        "Build intelligent applications using AI and modern technologies.",
      skills: ["Python", "Artificial Intelligence", "NLP"],
    },
    {
      icon: "📈",
      title: "Data Analyst",
      description:
        "Transform raw data into meaningful insights and reports.",
      skills: ["SQL", "Excel", "Power BI"],
    },
  ];

  const features = [
    {
      icon: "🎯",
      title: "AI Career Recommendations",
      description:
        "Discover career paths based on your skills, interests, and goals.",
    },
    {
      icon: "📋",
      title: "Skill Gap Analysis",
      description:
        "Identify your existing skills and the skills you need to develop.",
    },
    {
      icon: "🗺️",
      title: "Personalized Learning Roadmaps",
      description:
        "Follow a structured learning path to achieve your career goals.",
    },
  ];

  // Restore the login session when the page is refreshed.
  useEffect(() => {
    let cancelled = false;

    async function restoreSession() {
      const token = localStorage.getItem("careerNavigatorToken");

      if (!token) {
        if (!cancelled) {
          setCheckingSession(false);
        }
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const result = await response.json();

        if (!response.ok || !result.user) {
          throw new Error("Session is no longer valid.");
        }

        if (!cancelled) {
          setSession({
            token,
            user: result.user,
          });
          setPage("dashboard");
        }
      } catch {
        localStorage.removeItem("careerNavigatorToken");

        if (!cancelled) {
          setSession(null);
          setPage("home");
        }
      } finally {
        if (!cancelled) {
          setCheckingSession(false);
        }
      }
    }

    restoreSession();

    return () => {
      cancelled = true;
    };
  }, []);

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function openAuth() {
    setPage("auth");
    scrollToTop();
  }

  function openAssessment() {
    if (!session) {
      setPage("auth");
    } else {
      setPage("assessment");
    }

    scrollToTop();
  }

  function goHome() {
    setPage("home");
    scrollToTop();
  }

  function handleLogin(authSession) {
    localStorage.setItem(
      "careerNavigatorToken",
      authSession.token
    );

    setSession(authSession);
    setPage("dashboard");
    scrollToTop();
  }

  async function handleLogout() {
    const token = session?.token;

    // Clear the local session even if the backend is unavailable.
    localStorage.removeItem("careerNavigatorToken");
    setSession(null);
    setPage("home");
    scrollToTop();

    if (token) {
      try {
        await fetch(`${API_URL}/api/auth/logout`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error("Unable to notify backend about logout:", error);
      }
    }
  }

  if (checkingSession) {
    return (
      <div className="app-loading">
        <div className="app-loading-icon">C</div>
        <p>Loading Career Navigator...</p>
      </div>
    );
  }

  if (page === "auth") {
    return (
      <Auth
        onLogin={handleLogin}
        onBack={goHome}
      />
    );
  }

  if (page === "dashboard" && session) {
    return (
      <Dashboard
        session={session}
        onLogout={handleLogout}
        onNewAssessment={openAssessment}
      />
    );
  }

  if (page === "assessment") {
    return (
      <div className="assessment-screen">
        <button
          className="back-button"
          onClick={() => {
            setPage("dashboard");
            scrollToTop();
          }}
        >
          <span>←</span> Back to Dashboard
        </button>

        <CareerAssessment
          token={session?.token}
          onSessionExpired={() => {
            localStorage.removeItem("careerNavigatorToken");
            setSession(null);
            setPage("auth");
          }}
          onComplete={() => {
            setPage("dashboard");
            scrollToTop();
          }}
        />
      </div>
    );
  }

  // Original homepage.
  return (
    <div className="app">
      <header className="navbar">
        <a
          href="#home"
          className="logo"
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        >
          <span className="logo-icon">C</span>
          Career<span className="logo-blue">Navigator</span>
        </a>

        <nav className="nav-links">
          <a href="#home">Home</a>
          <a href="#features">Features</a>
          <a href="#careers">Explore Careers</a>
          <a href="#about">About</a>
        </nav>

        {session ? (
          <button
            className="nav-button"
            onClick={() => {
              setPage("dashboard");
              scrollToTop();
            }}
          >
            My Dashboard →
          </button>
        ) : (
          <button className="nav-button" onClick={openAuth}>
            Log In / Register →
          </button>
        )}
      </header>

      <main>
        <section className="hero" id="home">
          <div className="hero-content">
            <span className="announcement">
              <span>✦</span> YOUR FUTURE, POWERED BY AI
            </span>

            <h1>
              Discover Your
              <br />
              <span>Perfect Career</span>
              <br />
              With AI
            </h1>

            <p className="hero-description">
              Your skills have a future. Discover the right career,
              identify missing skills, and build a roadmap to success
              with AI-powered career guidance.
            </p>

            <div className="hero-actions">
              <button
                className="primary-button"
                onClick={openAssessment}
              >
                Find My Career →
              </button>

              <a href="#careers" className="secondary-button">
                Explore Careers
              </a>
            </div>

            <div className="trust-note">
              <span className="check-icon">✓</span>
              Personalized guidance for your career journey
            </div>
          </div>

          <div className="hero-visual">
            <div className="visual-glow"></div>

            <div className="career-window">
              <div className="window-header">
                <div className="window-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>

                <span>Career Insights</span>
                <span className="ai-label">✦ AI Preview</span>
              </div>

              <div className="profile-section">
                <div className="profile-avatar">👨‍💻</div>
                <div>
                  <h3>Your Career Potential</h3>
                  <p>Explore your possibilities</p>
                </div>
              </div>

              <div className="match-card">
                <div className="match-top">
                  <div className="match-icon">📊</div>
                  <div>
                    <h4>Data Scientist</h4>
                    <p>Example career recommendation</p>
                  </div>
                  <span className="match-badge">AI Preview</span>
                </div>

                <div className="match-progress">
                  <div className="progress-heading">
                    <span>Illustrative skill match</span>
                    <strong>85%</strong>
                  </div>

                  <div className="progress-track">
                    <div className="progress-fill"></div>
                  </div>
                </div>
              </div>

              <div className="skills-card">
                <h4>Skills to Develop</h4>

                <div className="skill-item">
                  <span>Python</span>
                  <span className="skill-completed">✓ Familiar</span>
                </div>

                <div className="skill-item">
                  <span>Machine Learning</span>
                  <span className="skill-pending">Learn next</span>
                </div>

                <div className="skill-item">
                  <span>Statistics</span>
                  <span className="skill-pending">Learn next</span>
                </div>
              </div>
            </div>

            <div className="floating-card floating-top">
              <span>✨</span>
              <div>
                <strong>Career clarity</strong>
                <p>One step at a time</p>
              </div>
            </div>

            <div className="floating-card floating-bottom">
              <span>🚀</span>
              <div>
                <strong>Keep growing</strong>
                <p>Your journey starts here</p>
              </div>
            </div>
          </div>
        </section>

        <section className="features-section" id="features">
          <div className="section-heading">
            <span className="section-label">WHAT WE OFFER</span>
            <h2>Your career journey, simplified</h2>
            <p>
              Everything you need to make informed career decisions
              and plan your professional future.
            </p>
          </div>

          <div className="features-grid">
            {features.map((feature) => (
              <article className="feature-card" key={feature.title}>
                <div className="feature-icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>

                <button
                  className="text-link"
                  onClick={openAssessment}
                >
                  Get started →
                </button>
              </article>
            ))}
          </div>
        </section>

        <section className="careers-section" id="careers">
          <div className="section-heading">
            <span className="section-label">EXPLORE POSSIBILITIES</span>
            <h2>Careers worth exploring</h2>
            <p>
              Explore exciting career opportunities in technology,
              artificial intelligence, and data science.
            </p>
          </div>

          <div className="careers-grid">
            {careers.map((career) => (
              <article className="career-card" key={career.title}>
                <div className="career-icon">{career.icon}</div>
                <h3>{career.title}</h3>
                <p>{career.description}</p>

                <div className="career-skills">
                  {career.skills.map((skill) => (
                    <span key={skill}>{skill}</span>
                  ))}
                </div>

                <button
                  className="career-link"
                  onClick={openAssessment}
                >
                  Find my career →
                </button>
              </article>
            ))}
          </div>
        </section>

        <section className="cta-section" id="get-started">
          <div className="cta-content">
            <span className="section-label">
              YOUR NEXT CHAPTER STARTS HERE
            </span>

            <h2>Ready to discover your career path?</h2>

            <p>
              Tell us about your skills, education, and interests.
              Start exploring career paths that match your goals.
            </p>

            <button
              className="primary-button"
              onClick={openAssessment}
            >
              Start My Journey →
            </button>
          </div>
        </section>
      </main>

      <footer className="footer" id="about">
        <a href="#home" className="logo">
          <span className="logo-icon">C</span>
          Career<span className="logo-blue">Navigator</span>
        </a>

        <p>Helping you navigate your future, one skill at a time.</p>

        <span className="copyright">
          © {CURRENT_YEAR} Career Navigator. All rights reserved.
        </span>
      </footer>
    </div>
  );
}

export default App;
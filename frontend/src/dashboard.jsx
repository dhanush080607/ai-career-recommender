import { useEffect, useState } from "react";
import "./dashboard.css";

const API_URL = "http://127.0.0.1:5000";

function formatJobSalary(minimum, maximum) {
  const formatAmount = (amount) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);

  if (minimum && maximum) {
    return `${formatAmount(minimum)} – ${formatAmount(maximum)}`;
  }
  if (minimum) {
    return `From ${formatAmount(minimum)}`;
  }
  if (maximum) {
    return `Up to ${formatAmount(maximum)}`;
  }
  return "";
}

async function resizeProfilePhoto(file) {
  if (!file.type.startsWith("image/")) {
    throw new Error("Choose an image file to use as your profile photo.");
  }
  if (file.size > 5 * 1024 * 1024) {
    throw new Error("Choose an image smaller than 5 MB.");
  }

  const sourceUrl = URL.createObjectURL(file);
  try {
    const image = new Image();
    image.src = sourceUrl;
    await image.decode();

    const scale = Math.min(1, 512 / Math.max(image.width, image.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(image.width * scale));
    canvas.height = Math.max(1, Math.round(image.height * scale));
    const context = canvas.getContext("2d");
    if (!context) {
      throw new Error("Your browser could not process this image.");
    }

    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.86);
  } finally {
    URL.revokeObjectURL(sourceUrl);
  }
}

function Dashboard({ session, onLogout, onNewAssessment }) {
  const [history, setHistory] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [profile, setProfile] = useState(session.user);
  const [avatarUrl, setAvatarUrl] = useState("");
  const [avatarVersion, setAvatarVersion] = useState(0);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [location, setLocation] = useState(session.user.location || "");
  const [locationSaving, setLocationSaving] = useState(false);
  const [locationSaved, setLocationSaved] = useState(false);
  const [jobsQuery, setJobsQuery] = useState("");
  const [jobs, setJobs] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [jobsSearched, setJobsSearched] = useState(false);
  const [jobsError, setJobsError] = useState("");
  const [jobsSetupUrl, setJobsSetupUrl] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadHistory() {
      setLoading(true);
      setError("");

      try {
        const [historyResponse, recommendationsResponse] = await Promise.all([
          fetch(`${API_URL}/api/assessments/history`, {
            headers: {
              Authorization: `Bearer ${session.token}`,
            },
          }),
          fetch(`${API_URL}/api/recommendations/history`, {
            headers: {
              Authorization: `Bearer ${session.token}`,
            },
          }),
        ]);

        const historyResult = await historyResponse.json();
        const recommendationsResult = await recommendationsResponse.json();

        if (historyResponse.status === 401 || recommendationsResponse.status === 401) {
          throw new Error(
            "Your session has expired. Please log in again."
          );
        }

        if (!historyResponse.ok) {
          throw new Error(
            historyResult.error || "Unable to load your assessment history."
          );
        }

        if (!recommendationsResponse.ok) {
          throw new Error(
            recommendationsResult.error || "Unable to load your career recommendations."
          );
        }

        if (!cancelled) {
          setHistory(historyResult.assessments || []);
          setRecommendations(recommendationsResult.recommendations || []);
          if (recommendationsResult.recommendations?.[0]?.careerName) {
            setJobsQuery((current) =>
              current || recommendationsResult.recommendations[0].careerName
            );
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, [session.token]);

  useEffect(() => {
    let cancelled = false;
    let imageUrl = "";

    async function loadAvatar() {
      if (!profile.hasProfilePhoto) {
        setAvatarUrl("");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/auth/avatar`, {
          headers: {
            Authorization: `Bearer ${session.token}`,
          },
        });
        if (!response.ok) {
          throw new Error("Unable to load your profile photo.");
        }

        imageUrl = URL.createObjectURL(await response.blob());
        if (!cancelled) {
          setAvatarUrl(imageUrl);
        }
      } catch {
        if (!cancelled) {
          setAvatarUrl("");
        }
      }
    }

    loadAvatar();
    return () => {
      cancelled = true;
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [profile.hasProfilePhoto, session.token, avatarVersion]);

  async function handlePhotoChange(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    setAvatarLoading(true);
    setProfileError("");
    try {
      const imageData = await resizeProfilePhoto(file);
      const response = await fetch(`${API_URL}/api/auth/avatar`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.token}`,
        },
        body: JSON.stringify({ imageData }),
      });
      const result = await response.json();

      if (response.status === 401) {
        onLogout();
        return;
      }
      if (!response.ok) {
        throw new Error(result.error || "Unable to update your profile photo.");
      }

      setProfile((current) => ({ ...current, hasProfilePhoto: true }));
      setAvatarVersion((version) => version + 1);
    } catch (photoError) {
      setProfileError(photoError.message || "Unable to update your profile photo.");
    } finally {
      setAvatarLoading(false);
    }
  }

  async function handleRemovePhoto() {
    setAvatarLoading(true);
    setProfileError("");
    try {
      const response = await fetch(`${API_URL}/api/auth/avatar`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${session.token}`,
        },
      });
      const result = await response.json();

      if (response.status === 401) {
        onLogout();
        return;
      }
      if (!response.ok) {
        throw new Error(result.error || "Unable to remove your profile photo.");
      }

      setProfile((current) => ({ ...current, hasProfilePhoto: false }));
      setAvatarUrl("");
    } catch (photoError) {
      setProfileError(photoError.message || "Unable to remove your profile photo.");
    } finally {
      setAvatarLoading(false);
    }
  }

  async function handleSaveLocation(event) {
    event.preventDefault();
    setLocationSaving(true);
    setLocationSaved(false);
    setProfileError("");

    try {
      const response = await fetch(`${API_URL}/api/auth/profile`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.token}`,
        },
        body: JSON.stringify({ location }),
      });
      const result = await response.json();

      if (response.status === 401) {
        onLogout();
        return;
      }
      if (!response.ok) {
        throw new Error(result.error || "Unable to save your job-search location.");
      }

      setProfile(result.user);
      setLocation(result.user.location || "");
      setLocationSaved(true);
    } catch (profileUpdateError) {
      setProfileError(
        profileUpdateError.message || "Unable to save your job-search location."
      );
    } finally {
      setLocationSaving(false);
    }
  }

  async function handleJobSearch(event) {
    event.preventDefault();
    setJobsError("");
    setJobsSetupUrl("");
    setJobsSearched(false);

    if (!location.trim()) {
      setJobsError("Add and save your city or postal code above to find nearby jobs.");
      return;
    }

    setJobsLoading(true);
    try {
      const parameters = new URLSearchParams({
        what: jobsQuery.trim() || "software developer",
        where: location.trim(),
      });
      const response = await fetch(`${API_URL}/api/jobs?${parameters}`, {
        headers: {
          Authorization: `Bearer ${session.token}`,
        },
      });
      const result = await response.json();

      if (response.status === 401) {
        onLogout();
        return;
      }
      if (!response.ok) {
        setJobsSetupUrl(result.setupUrl || "");
        throw new Error(result.error || "Unable to search live job listings.");
      }

      setJobs(result.jobs || []);
      setJobsSearched(true);
    } catch (searchError) {
      setJobsError(searchError.message || "Unable to search live job listings.");
    } finally {
      setJobsLoading(false);
    }
  }

  return (
    <div className="dashboard-page">
      <header className="dashboard-navbar">
        <a href="#dashboard" className="dashboard-logo">
          <span>C</span>
          Career<span className="dashboard-logo-blue">Navigator</span>
        </a>

        <div className="dashboard-user-actions">
          <div className="dashboard-avatar">
            {avatarUrl ? (
              <img src={avatarUrl} alt="" />
            ) : (
              profile.fullName?.charAt(0).toUpperCase() || "U"
            )}
          </div>
          <span className="dashboard-nav-profile-name">{profile.fullName}</span>

          <button
            className="dashboard-logout"
            onClick={onLogout}
          >
            Log Out
          </button>
        </div>
      </header>

      <main className="dashboard-main">
        <section className="dashboard-welcome">
          <span className="dashboard-eyebrow">
            YOUR PERSONAL CAREER SPACE
          </span>

          <h1>
            Welcome back, {profile.fullName?.split(" ")[0] || "Student"}! 👋
          </h1>

          <p>
            Explore your career possibilities and continue building
            your future, one skill at a time.
          </p>

          <button
            className="dashboard-primary-button"
            onClick={onNewAssessment}
          >
            Start New Assessment <span>→</span>
          </button>
        </section>

        <section className="dashboard-profile-card">
          <div className="dashboard-profile-avatar-wrap">
            <div className="dashboard-profile-icon">
              {avatarUrl ? (
                <img src={avatarUrl} alt={`${profile.fullName}'s profile`} />
              ) : (
                profile.fullName?.charAt(0).toUpperCase() || "U"
              )}
            </div>
            <label className="dashboard-photo-button">
              {avatarLoading ? "Saving photo..." : "Change photo"}
              <input
                type="file"
                accept="image/*"
                onChange={handlePhotoChange}
                disabled={avatarLoading}
                aria-label="Choose a profile photo"
              />
            </label>
            {profile.hasProfilePhoto && (
              <button
                className="dashboard-photo-remove"
                type="button"
                onClick={handleRemovePhoto}
                disabled={avatarLoading}
              >
                Remove
              </button>
            )}
          </div>

          <div className="dashboard-profile-info">
            <h2>{profile.fullName}</h2>
            <p>{profile.email}</p>
            <span>{profile.education}</span>
          </div>

          <div className="dashboard-profile-status">
            <span className="dashboard-status-dot"></span>
            Account Active
          </div>
        </section>

        <form className="dashboard-location-form" onSubmit={handleSaveLocation}>
          <div className="dashboard-location-copy">
            <span className="dashboard-eyebrow">PERSONALIZE YOUR SEARCH</span>
            <label htmlFor="job-location">Where should we look for jobs?</label>
            <p>Save your city or postal code to find relevant opportunities in India.</p>
          </div>
          <div className="dashboard-location-controls">
            <input
              id="job-location"
              type="text"
              value={location}
              onChange={(event) => {
                setLocation(event.target.value);
                setLocationSaved(false);
              }}
              maxLength={120}
              placeholder="e.g. Bengaluru, Karnataka"
            />
            <button type="submit" disabled={locationSaving}>
              {locationSaving ? "Saving..." : "Save location"}
            </button>
          </div>
          {locationSaved && (
            <p className="dashboard-location-saved" role="status">
              Job-search location saved.
            </p>
          )}
          {profileError && (
            <p className="dashboard-error dashboard-profile-error" role="alert">
              {profileError}
            </p>
          )}
        </form>

        <section className="dashboard-stats">
          <article className="dashboard-stat-card">
            <span className="dashboard-stat-icon">📋</span>
            <div>
              <p>Total Assessments</p>
              <h3>{loading ? "—" : history.length}</h3>
            </div>
          </article>

          <article className="dashboard-stat-card">
            <span className="dashboard-stat-icon">🎯</span>
            <div>
              <p>Career Recommendations</p>
              <h3>{loading ? "—" : recommendations.length}</h3>
            </div>
          </article>

          <article className="dashboard-stat-card">
            <span className="dashboard-stat-icon">🗺️</span>
            <div>
              <p>Roadmaps available</p>
              <h3>
                {loading
                  ? "—"
                  : recommendations.filter(
                      (item) => item.learningRoadmap?.length > 0
                    ).length}
              </h3>
            </div>
          </article>
        </section>

        <section className="dashboard-jobs-section">
          <div className="dashboard-section-heading">
            <div>
              <span className="dashboard-eyebrow">YOUR NEXT OPPORTUNITY</span>
              <h2>Jobs near you</h2>
              <p>Search live listings and apply directly through the job provider.</p>
            </div>
            {location && (
              <span className="dashboard-jobs-location">
                📍 {location}
              </span>
            )}
          </div>

          <form className="dashboard-jobs-search" onSubmit={handleJobSearch}>
            <label htmlFor="job-title">Job title or career</label>
            <div className="dashboard-jobs-search-controls">
              <input
                id="job-title"
                type="search"
                value={jobsQuery}
                onChange={(event) => setJobsQuery(event.target.value)}
                maxLength={100}
                placeholder="e.g. Data Analyst"
              />
              <button type="submit" disabled={jobsLoading}>
                {jobsLoading ? "Searching..." : "Search live jobs"}
              </button>
            </div>
          </form>

          {jobsError && (
            <div className="dashboard-jobs-error" role="alert">
              <p>{jobsError}</p>
              {jobsSetupUrl && (
                <a href={jobsSetupUrl} target="_blank" rel="noreferrer">
                  Get Adzuna API credentials →
                </a>
              )}
            </div>
          )}

          {jobsSearched && jobs.length === 0 && (
            <div className="dashboard-jobs-empty">
              No matching jobs were found. Try another job title or nearby city.
            </div>
          )}

          {jobs.length > 0 && (
            <div className="dashboard-jobs-grid">
              {jobs.map((job) => {
                const salary = formatJobSalary(job.salaryMin, job.salaryMax);
                return (
                  <article className="dashboard-job-card" key={job.id || job.applyUrl}>
                    <span className="dashboard-job-source">ADZUNA LISTING</span>
                    <h3>{job.title}</h3>
                    <p className="dashboard-job-company">{job.company}</p>
                    <p className="dashboard-job-meta">
                      📍 {job.location}
                      {job.contractTime && ` · ${job.contractTime.replaceAll("_", " ")}`}
                    </p>
                    {salary && <p className="dashboard-job-salary">{salary}</p>}
                    <p className="dashboard-job-description">{job.description}</p>
                    <a
                      className="dashboard-job-apply"
                      href={job.applyUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View job &amp; apply <span aria-hidden="true">↗</span>
                    </a>
                  </article>
                );
              })}
            </div>
          )}

          <p className="dashboard-jobs-attribution">
            Live job listings powered by{" "}
            <a href="https://www.adzuna.com/" target="_blank" rel="noreferrer">
              Adzuna
            </a>
            . Applications are completed on the job provider's website.
          </p>
        </section>

        <section className="dashboard-history-section">
          <div className="dashboard-section-heading">
            <div>
              <span className="dashboard-eyebrow">YOUR PROGRESS</span>
              <h2>Assessment History</h2>
              <p>Review the assessments saved to your account.</p>
            </div>

            <button
              className="dashboard-outline-button"
              onClick={onNewAssessment}
            >
              + New Assessment
            </button>
          </div>

          {loading ? (
            <div className="dashboard-message">
              Loading your assessment history...
            </div>
          ) : error ? (
            <div className="dashboard-error" role="alert">
              {error}
              <p>
                Your profile is available, but assessment history
                could not be loaded.
              </p>
            </div>
          ) : history.length === 0 ? (
            <div className="dashboard-empty">
              <div className="dashboard-empty-icon">📈</div>
              <h3>Your journey starts here</h3>
              <p>
                You haven't completed any assessments yet.
                Start your first assessment to begin tracking your career journey.
              </p>

              <button
                className="dashboard-primary-button"
                onClick={onNewAssessment}
              >
                Take My First Assessment →
              </button>
            </div>
          ) : (
            <div className="dashboard-history-list">
              {history.map((assessment) => {
                const linkedRecommendations = recommendations.filter(
                  (item) => Number(item.assessmentId) === Number(assessment.id)
                );

                return (
                  <article
                    className="dashboard-history-card"
                    key={assessment.id}
                  >
                    <div className="dashboard-history-content">
                      <div className="dashboard-assessment-heading">
                        <div className="dashboard-history-icon">📋</div>
                        <div>
                          <h3>Assessment #{assessment.id}</h3>
                          <p>
                            {new Date(assessment.createdAt).toLocaleString()}
                          </p>
                        </div>
                        <span className="dashboard-result-count">
                          {linkedRecommendations.length} career matches
                        </span>
                      </div>

                      {linkedRecommendations.length > 0 ? (
                        <div className="dashboard-recommendation-grid">
                          {linkedRecommendations.map((recommendation, index) => {
                            const score = Number(recommendation.matchScore);
                            const matchedSkills = recommendation.reasons
                              ?.matched_skills || [];
                            const missingSkills = recommendation.reasons
                              ?.missing_skills || [];
                            const roadmap = recommendation.learningRoadmap || [];

                            return (
                              <article
                                className={`dashboard-career-card${index === 0 ? " dashboard-career-card-featured" : ""}`}
                                key={`${assessment.id}-${recommendation.careerName}`}
                              >
                                <div className="dashboard-career-card-top">
                                  <span className="dashboard-career-rank">
                                    {index === 0 ? "BEST FIT" : `MATCH 0${index + 1}`}
                                  </span>
                                  {Number.isFinite(score) && (
                                    <span className="dashboard-match-score">
                                      {score.toFixed(0)}%
                                    </span>
                                  )}
                                </div>

                                <h4>{recommendation.careerName}</h4>
                                {recommendation.description && (
                                  <p className="dashboard-career-description">
                                    {recommendation.description}
                                  </p>
                                )}

                                {Number.isFinite(score) && (
                                  <div
                                    className="dashboard-match-track"
                                    role="meter"
                                    aria-label={`${score.toFixed(0)} percent career match`}
                                    aria-valuemin="0"
                                    aria-valuemax="100"
                                    aria-valuenow={Math.max(0, Math.min(100, score))}
                                  >
                                    <span
                                      style={{
                                        width: `${Math.max(0, Math.min(100, score))}%`,
                                      }}
                                    />
                                  </div>
                                )}

                                <div className="dashboard-skill-group">
                                  <span className="dashboard-skill-label">
                                    Skills you have
                                  </span>
                                  <div className="dashboard-skill-tags">
                                    {matchedSkills.length > 0 ? (
                                      matchedSkills.map((skill) => (
                                        <span className="dashboard-skill-tag dashboard-skill-tag-matched" key={skill}>
                                          {skill}
                                        </span>
                                      ))
                                    ) : (
                                      <span className="dashboard-skill-empty">
                                        Keep building your foundation
                                      </span>
                                    )}
                                  </div>
                                </div>

                                <div className="dashboard-skill-group">
                                  <span className="dashboard-skill-label">
                                    Skills to develop
                                  </span>
                                  <div className="dashboard-skill-tags">
                                    {missingSkills.length > 0 ? (
                                      missingSkills.map((skill) => (
                                        <span className="dashboard-skill-tag" key={skill}>
                                          {skill}
                                        </span>
                                      ))
                                    ) : (
                                      <span className="dashboard-skill-empty">
                                        No skill gaps identified
                                      </span>
                                    )}
                                  </div>
                                </div>

                                <details className="dashboard-roadmap">
                                  <summary>
                                    <span>View learning roadmap</span>
                                    <span className="dashboard-roadmap-chevron">⌄</span>
                                  </summary>
                                  {roadmap.length > 0 ? (
                                    <ol className="dashboard-roadmap-steps">
                                      {roadmap.map((step, stepIndex) => (
                                        <li key={`${step.step ?? stepIndex}-${step.topic}`}>
                                          <span className="dashboard-roadmap-step-number">
                                            {step.step ?? stepIndex + 1}
                                          </span>
                                          <div>
                                            <strong>{step.topic || "Learning step"}</strong>
                                            <p>
                                              {step.duration || "Self-paced"}
                                              {step.skills?.length
                                                ? ` · ${step.skills.join(", ")}`
                                                : ""}
                                            </p>
                                          </div>
                                        </li>
                                      ))}
                                    </ol>
                                  ) : (
                                    <p className="dashboard-roadmap-unavailable">
                                      A learning roadmap is not available for this career yet.
                                    </p>
                                  )}
                                </details>
                              </article>
                            );
                          })}
                        </div>
                      ) : (
                        <p className="dashboard-no-recommendations">
                          No career matches were saved for this assessment.
                        </p>
                      )}

                      <details className="dashboard-assessment-details">
                        <summary>View assessment profile</summary>
                        <div className="dashboard-assessment-facts">
                          <p><strong>Education</strong>{assessment.education}</p>
                          <p><strong>Proficiency</strong>{assessment.proficiency}</p>
                          <p><strong>Career goal</strong>{assessment.careerGoal}</p>
                          <p>
                            <strong>Skills</strong>
                            {assessment.skills.length
                              ? assessment.skills.join(", ")
                              : "None selected"}
                          </p>
                          <p>
                            <strong>Interests</strong>
                            {assessment.interests.length
                              ? assessment.interests.join(", ")
                              : "None selected"}
                          </p>
                        </div>
                      </details>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </main>

      <footer className="dashboard-footer">
        Career Navigator — Your future, one skill at a time.
      </footer>
    </div>
  );
}

export default Dashboard;

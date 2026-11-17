import base64
import binascii
import io
import os
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import generate_password_hash, check_password_hash

# Recommendation engine and curated career dataset
from career_dataset import get_career_by_name
from career_recommender import recommend_careers, analyze_skill_gap


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "career_navigator.db"
load_dotenv(BASE_DIR / ".env")

app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY",
    "development-only-change-this-secret-before-deployment"
)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 8
app.config["MAX_CONTENT_LENGTH"] = 800 * 1024
app.config["ADZUNA_APP_ID"] = os.environ.get("ADZUNA_APP_ID", "")
app.config["ADZUNA_APP_KEY"] = os.environ.get("ADZUNA_APP_KEY", "")

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5174",
            ]
        }
    },
)

jwt = JWTManager(app)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = get_db_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                education TEXT NOT NULL,
                location TEXT NOT NULL DEFAULT '',
                profile_photo BLOB,
                profile_photo_mime TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT NOT NULL,
                education TEXT NOT NULL,
                skills TEXT NOT NULL,
                interests TEXT NOT NULL,
                proficiency TEXT NOT NULL,
                career_goal TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                assessment_id INTEGER NOT NULL,
                career_name TEXT NOT NULL,
                match_score REAL,
                reasons TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (assessment_id)
                    REFERENCES assessments(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS learning_roadmaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                assessment_id INTEGER NOT NULL,
                career_name TEXT NOT NULL,
                roadmap TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (assessment_id)
                    REFERENCES assessments(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS revoked_tokens (
                jti TEXT PRIMARY KEY,
                revoked_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_assessments_user_id
                ON assessments(user_id);

            CREATE INDEX IF NOT EXISTS idx_recommendations_user_id
                ON recommendations(user_id);

            CREATE INDEX IF NOT EXISTS idx_roadmaps_user_id
                ON learning_roadmaps(user_id);
            """
        )

        user_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(users)")
        }
        if "location" not in user_columns:
            connection.execute(
                "ALTER TABLE users ADD COLUMN location TEXT NOT NULL DEFAULT ''"
            )
        if "profile_photo" not in user_columns:
            connection.execute("ALTER TABLE users ADD COLUMN profile_photo BLOB")
        if "profile_photo_mime" not in user_columns:
            connection.execute(
                "ALTER TABLE users ADD COLUMN profile_photo_mime TEXT"
            )

        connection.commit()

    finally:
        connection.close()


# Create the database and tables automatically.
init_db()


# --------------------------------------------------
# TOKEN AUTHENTICATION
# --------------------------------------------------

@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    connection = get_db_connection()

    try:
        token = connection.execute(
            "SELECT jti FROM revoked_tokens WHERE jti = ?",
            (jwt_payload["jti"],),
        ).fetchone()

        return token is not None

    finally:
        connection.close()


@jwt.unauthorized_loader
def missing_token(error):
    return jsonify({
        "success": False,
        "error": "Authentication required. Please log in."
    }), 401


@jwt.invalid_token_loader
def invalid_token(error):
    return jsonify({
        "success": False,
        "error": "Invalid authentication token."
    }), 401


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify({
        "success": False,
        "error": "Your session has expired. Please log in again."
    }), 401


@jwt.revoked_token_loader
def revoked_token(jwt_header, jwt_payload):
    return jsonify({
        "success": False,
        "error": "This session has been logged out. Please log in again."
    }), 401


# --------------------------------------------------
# CAREER DATA
# --------------------------------------------------

CAREERS = [
    {
        "id": 1,
        "title": "Data Scientist",
        "category": "Data Science",
        "description": (
            "Analyze data and build predictive models "
            "to solve real-world problems."
        ),
        "skills": [
            "Python",
            "Statistics",
            "SQL",
            "Machine Learning",
        ],
    },
    {
        "id": 2,
        "title": "AI Engineer",
        "category": "Artificial Intelligence",
        "description": (
            "Develop intelligent applications using "
            "machine learning and AI technologies."
        ),
        "skills": [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "Data Structures",
        ],
    },
    {
        "id": 3,
        "title": "Data Analyst",
        "category": "Data Analytics",
        "description": (
            "Explore datasets and communicate insights "
            "that support business decisions."
        ),
        "skills": [
            "SQL",
            "Python",
            "Data Analysis",
            "Statistics",
        ],
    },
    {
        "id": 4,
        "title": "Web Developer",
        "category": "Web Development",
        "description": (
            "Build responsive websites and interactive "
            "web applications."
        ),
        "skills": [
            "HTML & CSS",
            "JavaScript",
            "React",
            "APIs",
        ],
    },
    {
        "id": 5,
        "title": "Data Engineer",
        "category": "Data Engineering",
        "description": (
            "Design data pipelines and systems that "
            "collect, transform, and store data."
        ),
        "skills": [
            "Python",
            "SQL",
            "ETL",
            "Data Pipelines",
        ],
    },
]


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def current_time():
    return datetime.now(timezone.utc).isoformat()


def get_current_user_id():
    identity = get_jwt_identity()
    return int(identity)


def get_user_by_id(user_id):
    connection = get_db_connection()

    try:
        return connection.execute(
            """
            SELECT id, full_name, email, education, location,
                   profile_photo, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    finally:
        connection.close()


def user_to_dict(user):
    return {
        "id": user["id"],
        "fullName": user["full_name"],
        "email": user["email"],
        "education": user["education"],
        "location": user["location"],
        "hasProfilePhoto": user["profile_photo"] is not None,
        "createdAt": user["created_at"],
    }


# --------------------------------------------------
# GENERAL ENDPOINTS
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Welcome to AI Career Navigator API",
        "database": "SQLite",
        "authentication": "JWT",
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "success": True,
        "status": "healthy",
        "message": "AI Career Navigator backend is running."
    })


@app.route("/api/careers", methods=["GET"])
def get_careers():
    return jsonify({
        "success": True,
        "careers": CAREERS,
    })


@app.route("/api/careers/<int:career_id>", methods=["GET"])
def get_career(career_id):
    career = next(
        (item for item in CAREERS if item["id"] == career_id),
        None,
    )

    if career is None:
        return jsonify({
            "success": False,
            "error": "Career not found."
        }), 404

    return jsonify({
        "success": True,
        "career": career,
    })


# --------------------------------------------------
# USER REGISTRATION
# --------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Please submit valid JSON data."
        }), 400

    full_name = str(data.get("fullName", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    education = str(data.get("education", "")).strip()

    if not all([full_name, email, password, education]):
        return jsonify({
            "success": False,
            "error": "Name, email, password, and education are required."
        }), 400

    if len(full_name) > 100:
        return jsonify({
            "success": False,
            "error": "Name must be 100 characters or fewer."
        }), 400

    if len(email) > 254 or "@" not in email or email.startswith("@"):
        return jsonify({
            "success": False,
            "error": "Please enter a valid email address."
        }), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "success": False,
            "error": "Password must contain at least 8 characters."
        }), 400

    if len(password) > 128:
        return jsonify({
            "success": False,
            "error": "Password must contain 128 characters or fewer."
        }), 400

    password_hash = generate_password_hash(password)

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO users (
                full_name,
                email,
                password_hash,
                education,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                full_name,
                email,
                password_hash,
                education,
                current_time(),
            ),
        )

        connection.commit()
        user_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "error": "An account with this email already exists."
        }), 409

    finally:
        connection.close()

    access_token = create_access_token(
        identity=str(user_id)
    )

    user = get_user_by_id(user_id)

    return jsonify({
        "success": True,
        "message": "Registration successful.",
        "accessToken": access_token,
        "user": user_to_dict(user),
    }), 201


# --------------------------------------------------
# USER LOGIN
# --------------------------------------------------

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Please submit valid JSON data."
        }), 400

    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not email or not isinstance(password, str) or not password:
        return jsonify({
            "success": False,
            "error": "Email and password are required."
        }), 400

    connection = get_db_connection()

    try:
        user = connection.execute(
            """
            SELECT id, full_name, email, password_hash,
                   education, location, profile_photo, created_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    finally:
        connection.close()

    if user is None or not check_password_hash(
        user["password_hash"], password
    ):
        return jsonify({
            "success": False,
            "error": "Invalid email or password."
        }), 401

    access_token = create_access_token(
        identity=str(user["id"])
    )

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "accessToken": access_token,
        "user": user_to_dict(user),
    })


# --------------------------------------------------
# CURRENT USER PROFILE
# --------------------------------------------------

@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_my_profile():
    user_id = get_current_user_id()
    user = get_user_by_id(user_id)

    if user is None:
        return jsonify({
            "success": False,
            "error": "User account not found."
        }), 404

    return jsonify({
        "success": True,
        "user": user_to_dict(user),
    })


@app.route("/api/auth/profile", methods=["PATCH"])
@jwt_required()
def update_my_profile():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Please submit valid JSON data.",
        }), 400

    location = data.get("location")
    if not isinstance(location, str):
        return jsonify({
            "success": False,
            "error": "Location must be text.",
        }), 400

    location = location.strip()
    if len(location) > 120:
        return jsonify({
            "success": False,
            "error": "Location must be 120 characters or fewer.",
        }), 400

    user_id = get_current_user_id()
    connection = get_db_connection()
    try:
        connection.execute(
            "UPDATE users SET location = ? WHERE id = ?",
            (location, user_id),
        )
        connection.commit()
        user = connection.execute(
            """
            SELECT id, full_name, email, education, location,
                   profile_photo, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
    finally:
        connection.close()

    if user is None:
        return jsonify({
            "success": False,
            "error": "User account not found.",
        }), 404

    return jsonify({"success": True, "user": user_to_dict(user)})


@app.route("/api/auth/avatar", methods=["GET"])
@jwt_required()
def get_my_avatar():
    connection = get_db_connection()
    try:
        user = connection.execute(
            """
            SELECT profile_photo, profile_photo_mime
            FROM users
            WHERE id = ?
            """,
            (get_current_user_id(),),
        ).fetchone()
    finally:
        connection.close()

    if user is None:
        return jsonify({
            "success": False,
            "error": "User account not found.",
        }), 404
    if user["profile_photo"] is None:
        return jsonify({
            "success": False,
            "error": "No profile photo has been uploaded.",
        }), 404

    response = send_file(
        io.BytesIO(user["profile_photo"]),
        mimetype=user["profile_photo_mime"],
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "private, no-store"
    return response


@app.route("/api/auth/avatar", methods=["PUT"])
@jwt_required()
def upload_my_avatar():
    data = request.get_json(silent=True)
    image_data = data.get("imageData") if isinstance(data, dict) else None
    if not isinstance(image_data, str) or "," not in image_data:
        return jsonify({
            "success": False,
            "error": "Choose a valid JPEG, PNG, or WebP image.",
        }), 400

    header, encoded_image = image_data.split(",", 1)
    mime_type = header.removeprefix("data:").removesuffix(";base64")
    allowed_signatures = {
        "image/jpeg": lambda image: image.startswith(b"\xff\xd8\xff"),
        "image/png": lambda image: image.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": lambda image: (
            len(image) >= 12
            and image.startswith(b"RIFF")
            and image[8:12] == b"WEBP"
        ),
    }

    if mime_type not in allowed_signatures:
        return jsonify({
            "success": False,
            "error": "Only JPEG, PNG, and WebP images are supported.",
        }), 400

    try:
        image_bytes = base64.b64decode(encoded_image, validate=True)
    except (binascii.Error, ValueError):
        return jsonify({
            "success": False,
            "error": "The selected image could not be read.",
        }), 400

    if (
        not image_bytes
        or len(image_bytes) > 512 * 1024
        or not allowed_signatures[mime_type](image_bytes)
    ):
        return jsonify({
            "success": False,
            "error": "The image is invalid or too large. Choose an image under 512 KB.",
        }), 400

    connection = get_db_connection()
    try:
        cursor = connection.execute(
            """
            UPDATE users
            SET profile_photo = ?, profile_photo_mime = ?
            WHERE id = ?
            """,
            (image_bytes, mime_type, get_current_user_id()),
        )
        connection.commit()
    finally:
        connection.close()

    if cursor.rowcount == 0:
        return jsonify({
            "success": False,
            "error": "User account not found.",
        }), 404

    return jsonify({"success": True, "message": "Profile photo updated."})


@app.route("/api/auth/avatar", methods=["DELETE"])
@jwt_required()
def delete_my_avatar():
    connection = get_db_connection()
    try:
        cursor = connection.execute(
            """
            UPDATE users
            SET profile_photo = NULL, profile_photo_mime = NULL
            WHERE id = ?
            """,
            (get_current_user_id(),),
        )
        connection.commit()
    finally:
        connection.close()

    if cursor.rowcount == 0:
        return jsonify({
            "success": False,
            "error": "User account not found.",
        }), 404

    return jsonify({"success": True, "message": "Profile photo removed."})


@app.route("/api/jobs", methods=["GET"])
@jwt_required()
def search_jobs():
    location = request.args.get("where", "").strip()
    query = request.args.get("what", "software developer").strip()

    if not location:
        return jsonify({
            "success": False,
            "error": "Add your city or postal code to your profile before searching for jobs.",
        }), 400
    if len(location) > 120 or len(query) > 100:
        return jsonify({
            "success": False,
            "error": "Keep the location under 120 characters and the job title under 100 characters.",
        }), 400
    if not app.config["ADZUNA_APP_ID"] or not app.config["ADZUNA_APP_KEY"]:
        return jsonify({
            "success": False,
            "error": (
                "Live job search needs Adzuna API credentials. Create an Adzuna developer "
                "account, then add ADZUNA_APP_ID and ADZUNA_APP_KEY to backend/.env."
            ),
            "setupUrl": "https://developer.adzuna.com/signup",
        }), 503

    parameters = urlencode({
        "app_id": app.config["ADZUNA_APP_ID"],
        "app_key": app.config["ADZUNA_APP_KEY"],
        "what": query or "software developer",
        "where": location,
        "results_per_page": 12,
        "content-type": "application/json",
    })
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?{parameters}"
    api_request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(api_request, timeout=12) as response:
            payload = json.loads(response.read())
    except HTTPError as error:
        app.logger.warning("Adzuna job search returned HTTP %s.", error.code)
        return jsonify({
            "success": False,
            "error": "The live job provider could not complete your search. Please try again later.",
        }), 502
    except (URLError, TimeoutError, json.JSONDecodeError):
        app.logger.warning("Adzuna job search could not be completed.")
        return jsonify({
            "success": False,
            "error": "Could not reach the live job provider. Check your connection and try again.",
        }), 502

    jobs = []
    for item in payload.get("results", []):
        if not isinstance(item, dict):
            continue
        apply_url = item.get("redirect_url", "")
        parsed_url = urlparse(apply_url)
        if parsed_url.scheme not in {"https", "http"} or not parsed_url.netloc:
            continue

        company = item.get("company") or {}
        job_location = item.get("location") or {}
        jobs.append({
            "id": str(item.get("id", "")),
            "title": item.get("title", "Job listing"),
            "company": company.get("display_name", "Company not listed"),
            "location": job_location.get("display_name", location),
            "description": item.get("description", ""),
            "applyUrl": apply_url,
            "salaryMin": item.get("salary_min"),
            "salaryMax": item.get("salary_max"),
            "contractTime": item.get("contract_time", ""),
            "created": item.get("created", ""),
        })

    return jsonify({
        "success": True,
        "count": len(jobs),
        "where": location,
        "what": query or "software developer",
        "jobs": jobs,
    })


# --------------------------------------------------
# USER LOGOUT
# --------------------------------------------------

@app.route("/api/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    token_id = get_jwt()["jti"]

    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT OR IGNORE INTO revoked_tokens (jti, revoked_at)
            VALUES (?, ?)
            """,
            (token_id, current_time()),
        )

        connection.commit()

    finally:
        connection.close()

    return jsonify({
        "success": True,
        "message": "Logout successful."
    })


# --------------------------------------------------
# CAREER ASSESSMENT
# --------------------------------------------------

@app.route("/api/assess", methods=["POST"])
@jwt_required(optional=True)
def assess_career():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Please submit valid JSON data."
        }), 400

    required_fields = [
        "fullName",
        "education",
        "skills",
        "interests",
        "proficiency",
        "careerGoal",
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400

    full_name = str(data["fullName"]).strip()
    education = str(data["education"]).strip()
    proficiency = str(data["proficiency"]).strip()
    career_goal = str(data["careerGoal"]).strip()
    skills = data["skills"]
    interests = data["interests"]

    if not full_name or not education or not proficiency or not career_goal:
        return jsonify({
            "success": False,
            "error": "Please complete all required fields."
        }), 400

    if not isinstance(skills, list) or not isinstance(interests, list):
        return jsonify({
            "success": False,
            "error": "Skills and interests must be lists."
        }), 400

    if not all(isinstance(item, str) for item in skills + interests):
        return jsonify({
            "success": False,
            "error": "Skills and interests must contain text values."
        }), 400

    if len(skills) > 50 or len(interests) > 50:
        return jsonify({
            "success": False,
            "error": "Too many skills or interests were submitted."
        }), 400

    # Existing frontend submissions are temporarily accepted
    # without login. When a valid token is supplied, the record
    # is associated with the authenticated user.
    identity = get_jwt_identity()
    user_id = int(identity) if identity is not None else None

    if user_id is not None and get_user_by_id(user_id) is None:
        return jsonify({
            "success": False,
            "error": "User account not found. Please log in again."
        }), 401

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO assessments (
                user_id,
                full_name,
                education,
                skills,
                interests,
                proficiency,
                career_goal,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                full_name,
                education,
                json.dumps(skills),
                json.dumps(interests),
                proficiency,
                career_goal,
                current_time(),
            ),
        )

        connection.commit()
        assessment_id = cursor.lastrowid

    finally:
        connection.close()

    return jsonify({
        "success": True,
        "message": "Assessment received and saved successfully.",
        "assessmentId": assessment_id,
        "associatedWithAccount": user_id is not None,
        "assessment": {
            "fullName": full_name,
            "education": education,
            "skills": skills,
            "interests": interests,
            "proficiency": proficiency,
            "careerGoal": career_goal,
        },
    }), 201


# --------------------------------------------------
# CAREER RECOMMENDATIONS
# --------------------------------------------------

@app.route("/api/recommendations", methods=["POST"])
@jwt_required()
def create_recommendations():
    """Score careers for the logged-in student and save the results."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Please submit valid JSON data."}), 400

    full_name = str(data.get("fullName", "")).strip()
    education = str(data.get("education", "")).strip()
    proficiency = str(data.get("proficiency", "")).strip()
    career_goal = str(data.get("careerGoal", "")).strip()
    skills = data.get("skills", [])
    interests = data.get("interests", [])
    assessment_id = data.get("assessmentId")
    top_n = data.get("top_n", data.get("topN", 5))

    if not all([full_name, education, proficiency, career_goal]):
        return jsonify({"success": False, "error": "Name, education, proficiency, and career goal are required."}), 400
    if not isinstance(skills, list) or not isinstance(interests, list):
        return jsonify({"success": False, "error": "Skills and interests must be lists."}), 400
    if not all(isinstance(item, str) for item in skills + interests):
        return jsonify({"success": False, "error": "Skills and interests must contain text values."}), 400
    if len(skills) > 50 or len(interests) > 50:
        return jsonify({"success": False, "error": "Too many skills or interests were submitted."}), 400
    try:
        top_n = max(1, min(int(top_n), 8))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "top_n must be a number."}), 400

    user_id = get_current_user_id()
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"success": False, "error": "User account not found. Please log in again."}), 401

    profile = {
        "fullName": full_name,
        "education": education,
        "skills": skills,
        "interests": interests,
        "proficiency": proficiency,
        "careerGoal": career_goal,
        "full_name": full_name,
        "career_goal": career_goal,
    }

    try:
        ranked_result = recommend_careers(profile, top_n=top_n)
        recommendations = ranked_result.get("recommendations", []) if isinstance(ranked_result, dict) else []
    except (TypeError, ValueError, KeyError):
        app.logger.exception("Career recommendation failed")
        return jsonify({"success": False, "error": "Could not generate recommendations. Check the submitted profile values."}), 400
    except Exception:
        app.logger.exception("Unexpected recommendation engine error")
        return jsonify({"success": False, "error": "The recommendation engine encountered an error."}), 500

    connection = get_db_connection()
    try:
        if assessment_id is not None:
            existing_assessment = connection.execute(
                "SELECT id FROM assessments WHERE id = ? AND user_id = ?",
                (int(assessment_id), user_id),
            ).fetchone()
            if existing_assessment is None:
                return jsonify({"success": False, "error": "Assessment not found for this account."}), 404
            assessment_record_id = int(existing_assessment["id"])
        else:
            cursor = connection.execute(
                """INSERT INTO assessments
                   (user_id, full_name, education, skills, interests, proficiency, career_goal, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, full_name, education, json.dumps(skills), json.dumps(interests), proficiency, career_goal, current_time()),
            )
            assessment_record_id = cursor.lastrowid

        saved_recommendations = []
        for item in recommendations:
            if not isinstance(item, dict):
                continue
            career_name = str(item.get("career_name", item.get("career", item.get("title", item.get("name", "Unknown career")))))
            raw_score = item.get("match_score", item.get("score", item.get("match_percentage", 0)))
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                score = 0.0
            reasons = {
                "matched_skills": item.get("matched_skills", item.get("matchedSkills", [])),
                "missing_skills": item.get("missing_skills", item.get("missingSkills", [])),
                "matched_interests": item.get("matched_interests", item.get("matchedInterests", [])),
            }
            connection.execute(
                """INSERT INTO recommendations
                   (user_id, assessment_id, career_name, match_score, reasons, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, assessment_record_id, career_name, score, json.dumps(reasons), current_time()),
            )
            roadmap = item.get("learning_roadmap", item.get("roadmap", []))
            if roadmap:
                connection.execute(
                    """INSERT INTO learning_roadmaps
                       (user_id, assessment_id, career_name, roadmap, created_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, assessment_record_id, career_name, json.dumps(roadmap), current_time()),
                )
            saved_recommendations.append({**item, "career_name": career_name, "match_score": score})

        connection.commit()
    except Exception:
        connection.rollback()
        app.logger.exception("Could not save career recommendations")
        return jsonify({"success": False, "error": "Could not save the assessment and recommendations."}), 500
    finally:
        connection.close()

    return jsonify({
        "success": True,
        "message": "Career recommendations generated successfully.",
        "assessmentId": assessment_record_id,
        "count": len(saved_recommendations),
        "recommendations": saved_recommendations,
        "weights": {"skills": 50, "interests": 30, "career_goal": 15, "proficiency": 5},
    }), 201


@app.route("/api/recommendations/history", methods=["GET"])
@jwt_required()
def get_recommendations_history():
    user_id = get_current_user_id()
    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                r.assessment_id,
                r.career_name,
                r.match_score,
                r.reasons,
                r.created_at,
                (
                    SELECT roadmap
                    FROM learning_roadmaps
                    WHERE user_id = r.user_id
                      AND assessment_id = r.assessment_id
                      AND career_name = r.career_name
                    ORDER BY id DESC
                    LIMIT 1
                ) AS learning_roadmap
            FROM recommendations AS r
            WHERE r.user_id = ?
            ORDER BY r.assessment_id DESC, r.id ASC
            """,
            (user_id,),
        ).fetchall()
    finally:
        connection.close()

    recommendations = []
    for row in rows:
        reasons = json.loads(row["reasons"]) if row["reasons"] else {}
        roadmap = (
            json.loads(row["learning_roadmap"])
            if row["learning_roadmap"]
            else None
        )
        career = get_career_by_name(row["career_name"])
        if not roadmap and career:
            roadmap = career["learning_roadmap"]

        recommendations.append({
            "assessmentId": row["assessment_id"],
            "careerName": row["career_name"],
            "matchScore": row["match_score"],
            "reasons": reasons,
            "description": career["description"] if career else "",
            "careerLevel": career["career_level"] if career else "",
            "learningRoadmap": roadmap or [],
            "createdAt": row["created_at"],
        })

    return jsonify({
        "success": True,
        "count": len(recommendations),
        "recommendations": recommendations,
        "latest": recommendations[0] if recommendations else None,
    })


# --------------------------------------------------
# SKILL-GAP ANALYSIS
# --------------------------------------------------

@app.route("/api/skill-gap", methods=["POST"])
@jwt_required()
def get_skill_gap():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Please submit valid JSON data."}), 400

    skills = data.get("skills", [])
    career_name = str(data.get("career_name", data.get("careerName", ""))).strip()
    if not isinstance(skills, list) or not all(isinstance(item, str) for item in skills):
        return jsonify({"success": False, "error": "Skills must be a list of text values."}), 400
    if not career_name:
        return jsonify({"success": False, "error": "career_name is required."}), 400

    if get_user_by_id(get_current_user_id()) is None:
        return jsonify({"success": False, "error": "User account not found. Please log in again."}), 401

    try:
        result = analyze_skill_gap(skills, career_name)
    except (TypeError, ValueError, KeyError) as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception:
        app.logger.exception("Skill-gap analysis failed")
        return jsonify({"success": False, "error": "Could not analyze the skill gap."}), 500

    return jsonify({"success": True, "skillGap": result})


# --------------------------------------------------
# AUTHENTICATED USER ASSESSMENT HISTORY
# --------------------------------------------------

@app.route("/api/assessments/history", methods=["GET"])
@jwt_required()
def assessment_history():
    user_id = get_current_user_id()

    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT id, full_name, education, skills, interests,
                   proficiency, career_goal, created_at
            FROM assessments
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()

    finally:
        connection.close()

    history = []

    for row in rows:
        history.append({
            "id": row["id"],
            "fullName": row["full_name"],
            "education": row["education"],
            "skills": json.loads(row["skills"]),
            "interests": json.loads(row["interests"]),
            "proficiency": row["proficiency"],
            "careerGoal": row["career_goal"],
            "createdAt": row["created_at"],
        })

    return jsonify({
        "success": True,
        "count": len(history),
        "assessments": history,
    })


# --------------------------------------------------
# ERROR HANDLERS
# --------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "API endpoint not found."
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.exception("Unexpected server error")

    return jsonify({
        "success": False,
        "error": "An internal server error occurred."
    }), 500


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":
    print("=" * 45)
    print("       AI CAREER NAVIGATOR API")
    print("=" * 45)
    print(f"Backend:  http://127.0.0.1:5000")
    print(f"Health:   http://127.0.0.1:5000/api/health")
    print(f"Careers:  http://127.0.0.1:5000/api/careers")
    print(f"Database: {DATABASE_PATH}")
    print("=" * 45)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
"""
AI Career Navigator
Career Recommendation Engine

This module:
1. Evaluates student skills.
2. Matches student interests with careers.
3. Considers proficiency and career goals.
4. Calculates career match scores.
5. Identifies missing skills.
6. Ranks careers by suitability.

The engine uses a weighted scoring algorithm based on
the manually curated career dataset.
"""

from career_dataset import (
    get_all_careers,
    get_all_skill_names,
    get_all_interests
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

# Weights determine the contribution of each factor.
SKILL_WEIGHT = 0.50
INTEREST_WEIGHT = 0.30
GOAL_WEIGHT = 0.15
PROFICIENCY_WEIGHT = 0.05


PROFICIENCY_LEVELS = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3
}


# --------------------------------------------------
# INPUT NORMALIZATION
# --------------------------------------------------

def normalize_list(values):
    """
    Convert a list of strings to normalized lowercase values.
    Remove extra spaces and duplicate entries.
    """

    if not isinstance(values, list):
        return []

    normalized_values = []

    for value in values:
        if isinstance(value, str):
            cleaned_value = value.strip().lower()

            if cleaned_value and cleaned_value not in normalized_values:
                normalized_values.append(cleaned_value)

    return normalized_values


def normalize_text(value):
    """
    Normalize a text value.
    """

    if not isinstance(value, str):
        return ""

    return value.strip().lower()


# --------------------------------------------------
# INPUT VALIDATION
# --------------------------------------------------

def validate_student_profile(profile):
    """
    Validate the student's profile before calculating recommendations.
    """

    if not isinstance(profile, dict):
        raise ValueError("Student profile must be a dictionary.")

    skills = profile.get("skills", [])
    interests = profile.get("interests", [])
    proficiency = profile.get("proficiency", "beginner")
    career_goal = profile.get("career_goal", "")

    if not isinstance(skills, list):
        raise ValueError("Skills must be provided as a list.")

    if not isinstance(interests, list):
        raise ValueError("Interests must be provided as a list.")

    if not isinstance(proficiency, str):
        raise ValueError("Proficiency must be a string.")

    if not isinstance(career_goal, str):
        raise ValueError("Career goal must be a string.")

    normalized_skills = normalize_list(skills)
    normalized_interests = normalize_list(interests)

    known_skills = {
        skill.lower()
        for skill in get_all_skill_names()
    }

    known_interests = {
        interest.lower()
        for interest in get_all_interests()
    }

    unknown_skills = [
        skill
        for skill in normalized_skills
        if skill not in known_skills
    ]

    unknown_interests = [
        interest
        for interest in normalized_interests
        if interest not in known_interests
    ]

    return {
        "skills": normalized_skills,
        "interests": normalized_interests,
        "proficiency": normalize_text(proficiency),
        "career_goal": normalize_text(career_goal),
        "unknown_skills": unknown_skills,
        "unknown_interests": unknown_interests
    }


# --------------------------------------------------
# SKILL MATCHING
# --------------------------------------------------

def calculate_skill_match(student_skills, required_skills):
    """
    Calculate the percentage of required skills matched by the student.

    Formula:
        matched required skills / total required skills * 100
    """

    required = {
        skill.lower()
        for skill in required_skills
    }

    matched = required.intersection(student_skills)
    missing = required - student_skills

    if not required:
        score = 0.0
    else:
        score = (len(matched) / len(required)) * 100

    return {
        "score": round(score, 2),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing)
    }


# --------------------------------------------------
# INTEREST MATCHING
# --------------------------------------------------

def calculate_interest_match(student_interests, career_interests):
    """
    Calculate the percentage of career interests matching
    the student's selected interests.
    """

    required_interests = {
        interest.lower()
        for interest in career_interests
    }

    matched = required_interests.intersection(student_interests)

    if not required_interests:
        score = 0.0
    else:
        score = (
            len(matched) / len(required_interests)
        ) * 100

    return {
        "score": round(score, 2),
        "matched_interests": sorted(matched)
    }


# --------------------------------------------------
# CAREER GOAL MATCHING
# --------------------------------------------------

def calculate_goal_match(student_goal, career_name):
    """
    Give a full goal score when the student's selected career goal
    matches a career name.

    A partial score is given when the goal is empty or unspecified.
    """

    if not student_goal:
        return 50.0

    if student_goal == career_name.lower():
        return 100.0

    return 0.0


# --------------------------------------------------
# PROFICIENCY MATCHING
# --------------------------------------------------

def calculate_proficiency_match(student_proficiency, career_level):
    """
    Calculate a small proficiency compatibility score.

    Entry-level careers are suitable for beginners.
    Intermediate careers receive higher scores when the student
    has intermediate or advanced proficiency.

    This is a heuristic, not a formal hiring requirement.
    """

    student_level = PROFICIENCY_LEVELS.get(
        student_proficiency,
        1
    )

    career_level = normalize_text(career_level)

    if career_level == "entry level":
        if student_level == 1:
            return 100.0

        if student_level == 2:
            return 90.0

        return 80.0

    if career_level == "intermediate":
        if student_level == 1:
            return 60.0

        if student_level == 2:
            return 100.0

        return 100.0

    return 50.0


# --------------------------------------------------
# SCORE CALCULATION
# --------------------------------------------------

def calculate_career_score(profile, career):
    """
    Calculate the weighted match score for one career.
    """

    skill_result = calculate_skill_match(
        set(profile["skills"]),
        career["required_skills"]
    )

    interest_result = calculate_interest_match(
        set(profile["interests"]),
        career["interests"]
    )

    goal_score = calculate_goal_match(
        profile["career_goal"],
        career["career_name"]
    )

    proficiency_score = calculate_proficiency_match(
        profile["proficiency"],
        career["career_level"]
    )

    final_score = (
        skill_result["score"] * SKILL_WEIGHT
        + interest_result["score"] * INTEREST_WEIGHT
        + goal_score * GOAL_WEIGHT
        + proficiency_score * PROFICIENCY_WEIGHT
    )

    final_score = round(
        max(0.0, min(100.0, final_score)),
        2
    )

    return {
        "career_id": career["career_id"],
        "career_name": career["career_name"],
        "description": career["description"],
        "match_score": final_score,
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "skill_match_score": skill_result["score"],
        "interest_match_score": interest_result["score"],
        "goal_match_score": goal_score,
        "proficiency_match_score": proficiency_score,
        "matched_interests": interest_result["matched_interests"],
        "required_skills": career["required_skills"],
        "career_level": career["career_level"],
        "learning_roadmap": career["learning_roadmap"]
    }


# --------------------------------------------------
# RECOMMENDATION ENGINE
# --------------------------------------------------

def recommend_careers(student_profile, top_n=5):
    """
    Recommend the top N careers for a student.

    Parameters:
        student_profile (dict):
            {
                "skills": ["Python", "SQL"],
                "interests": ["Data Analysis"],
                "proficiency": "Intermediate",
                "career_goal": "Data Scientist"
            }

        top_n (int):
            Number of recommendations to return.

    Returns:
        Dictionary containing ranked careers and validation information.
    """

    if (
        not isinstance(top_n, int)
        or isinstance(top_n, bool)
        or top_n < 1
    ):
        raise ValueError("top_n must be a positive integer.")

    profile = validate_student_profile(student_profile)

    careers = get_all_careers()

    recommendations = []

    for career in careers:
        result = calculate_career_score(
            profile,
            career
        )

        recommendations.append(result)

    # Sort by score from highest to lowest.
    # Career ID provides deterministic tie-breaking.
    recommendations.sort(
        key=lambda item: (
            -item["match_score"],
            item["career_id"]
        )
    )

    ranked_recommendations = recommendations[:top_n]

    return {
        "success": True,
        "total_careers_evaluated": len(careers),
        "recommendations": ranked_recommendations,
        "profile_validation": {
            "unknown_skills": profile["unknown_skills"],
            "unknown_interests": profile["unknown_interests"]
        },
        "scoring_weights": {
            "skills": SKILL_WEIGHT,
            "interests": INTEREST_WEIGHT,
            "career_goal": GOAL_WEIGHT,
            "proficiency": PROFICIENCY_WEIGHT
        }
    }


# --------------------------------------------------
# SKILL GAP ANALYSIS
# --------------------------------------------------

def analyze_skill_gap(student_skills, career_name):
    """
    Identify skills a student is missing for a selected career.
    """

    if not isinstance(career_name, str) or not career_name.strip():
        raise ValueError("Career name must be a non-empty string.")

    if not isinstance(student_skills, list):
        raise ValueError("Student skills must be provided as a list.")

    normalized_skills = normalize_list(student_skills)

    for skill in normalized_skills:
        if skill not in {
            item.lower()
            for item in get_all_skill_names()
        }:
            raise ValueError(
                f"Unknown skill: {skill}. "
                "Please use a skill from the career dataset."
            )

    career = None

    for item in get_all_careers():
        if item["career_name"].lower() == career_name.strip().lower():
            career = item
            break

    if career is None:
        raise ValueError(
            f"Career '{career_name}' was not found in the dataset."
        )

    skill_result = calculate_skill_match(
        set(normalized_skills),
        career["required_skills"]
    )

    return {
        "career_name": career["career_name"],
        "skill_match_score": skill_result["score"],
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "total_required_skills": len(career["required_skills"]),
        "total_matched_skills": len(skill_result["matched_skills"]),
        "total_missing_skills": len(skill_result["missing_skills"])
    }


# --------------------------------------------------
# TESTING
# --------------------------------------------------

if __name__ == "__main__":

    student = {
        "skills": [
            "Python",
            "SQL",
            "Statistics"
        ],
        "interests": [
            "Data Analysis",
            "Artificial Intelligence",
            "Problem Solving"
        ],
        "proficiency": "Intermediate",
        "career_goal": "Data Scientist"
    }

    print("=" * 65)
    print("AI CAREER NAVIGATOR - RECOMMENDATION ENGINE")
    print("=" * 65)

    print("\nStudent Profile:")
    print(f"Skills: {', '.join(student['skills'])}")
    print(f"Interests: {', '.join(student['interests'])}")
    print(f"Proficiency: {student['proficiency']}")
    print(f"Career Goal: {student['career_goal']}")

    result = recommend_careers(
        student_profile=student,
        top_n=5
    )

    print("\nTOP CAREER RECOMMENDATIONS")
    print("-" * 65)

    for index, career in enumerate(
        result["recommendations"],
        start=1
    ):
        print(f"\nRank: {index}")
        print(f"Career: {career['career_name']}")
        print(f"Match Score: {career['match_score']}%")
        print(
            "Matched Skills: "
            + (
                ", ".join(career["matched_skills"])
                if career["matched_skills"]
                else "None"
            )
        )
        print(
            "Missing Skills: "
            + (
                ", ".join(career["missing_skills"])
                if career["missing_skills"]
                else "None"
            )
        )

    print("\nSKILL GAP ANALYSIS")
    print("-" * 65)

    gap = analyze_skill_gap(
        student_skills=student["skills"],
        career_name="Data Scientist"
    )

    print(f"Career: {gap['career_name']}")
    print(f"Skill Match: {gap['skill_match_score']}%")
    print(f"Matched Skills: {gap['matched_skills']}")
    print(f"Missing Skills: {gap['missing_skills']}")

    print("\nRecommendation engine tested successfully!")
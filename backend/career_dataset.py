"""
AI Career Navigator
Career Dataset

This module contains structured information about career paths,
required skills, interests, proficiency levels, and learning roadmaps.

The dataset will be used by the career recommendation engine
and skill gap analysis system.
"""

CAREER_DATASET = [
    {
        "career_id": 1,
        "career_name": "Data Scientist",
        "description": (
            "Analyzes complex datasets and develops statistical "
            "models to discover patterns and support decision-making."
        ),
        "required_skills": [
            "Python",
            "Statistics",
            "Machine Learning",
            "SQL",
            "Data Visualization"
        ],
        "interests": [
            "Data Analysis",
            "Mathematics",
            "Artificial Intelligence",
            "Problem Solving",
            "Research"
        ],
        "minimum_proficiency": "Intermediate",
        "career_level": "Intermediate",
        "learning_roadmap": [
            {
                "step": 1,
                "topic": "Python Programming",
                "skills": ["Python"],
                "duration": "3 weeks"
            },
            {
                "step": 2,
                "topic": "Statistics and Mathematics",
                "skills": ["Statistics"],
                "duration": "3 weeks"
            },
            {
                "step": 3,
                "topic": "SQL and Data Analysis",
                "skills": ["SQL", "Data Analysis"],
                "duration": "3 weeks"
            },
            {
                "step": 4,
                "topic": "Machine Learning",
                "skills": ["Machine Learning"],
                "duration": "4 weeks"
            },
            {
                "step": 5,
                "topic": "Data Visualization and Projects",
                "skills": ["Data Visualization"],
                "duration": "3 weeks"
            }
        ]
    },

    {
        "career_id": 2,
        "career_name": "AI Engineer",
        "description": (
            "Designs and develops artificial intelligence systems "
            "using machine learning, deep learning, and programming."
        ),
        "required_skills": [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "Mathematics",
            "Problem Solving"
        ],
        "interests": [
            "Artificial Intelligence",
            "Automation",
            "Machine Learning",
            "Innovation",
            "Problem Solving"
        ],
        "minimum_proficiency": "Intermediate",
        "career_level": "Intermediate",
        "learning_roadmap": [
            {
                "step": 1,
                "topic": "Python Programming",
                "skills": ["Python"],
                "duration": "3 weeks"
            },
            {
                "step": 2,
                "topic": "Mathematics for AI",
                "skills": ["Mathematics"],
                "duration": "4 weeks"
            },
            {
                "step": 3,
                "topic": "Machine Learning Fundamentals",
                "skills": ["Machine Learning"],
                "duration": "4 weeks"
            },
            {
                "step": 4,
                "topic": "Deep Learning",
                "skills": ["Deep Learning"],
                "duration": "4 weeks"
            },
            {
                "step": 5,
                "topic": "AI Projects",
                "skills": ["Problem Solving"],
                "duration": "3 weeks"
            }
        ]
    },

    {
        "career_id": 3,
        "career_name": "Data Analyst",
        "description": (
            "Collects, cleans, analyzes, and visualizes data "
            "to help organizations make informed decisions."
        ),
        "required_skills": [
            "SQL",
            "Excel",
            "Python",
            "Statistics",
            "Data Visualization"
        ],
        "interests": [
            "Data Analysis",
            "Business Intelligence",
            "Problem Solving",
            "Research",
            "Statistics"
        ],
        "minimum_proficiency": "Beginner",
        "career_level": "Entry Level",
        "learning_roadmap": [
            {
                "step": 1,
                "topic": "Excel Fundamentals",
                "skills": ["Excel"],
                "duration": "2 weeks"
            },
            {
                "step": 2,
                "topic": "SQL Fundamentals",
                "skills": ["SQL"],
                "duration": "3 weeks"
            },
            {
                "step": 3,
                "topic": "Python for Data Analysis",
                "skills": ["Python"],
                "duration": "3 weeks"
            },
            {
                "step": 4,
                "topic": "Statistics",
                "skills": ["Statistics"],
                "duration": "2 weeks"
            },
            {
                "step": 5,
                "topic": "Data Visualization Projects",
                "skills": ["Data Visualization"],
                "duration": "3 weeks"
            }
        ]
    },

    {
        "career_id": 4,
        "career_name": "Web Developer",
        "description": (
            "Builds and maintains websites and web applications "
            "using frontend and backend technologies."
        ),
        "required_skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "Problem Solving"
        ],
        "interests": [
            "Web Development",
            "UI Design",
            "Application Development",
            "Creativity",
            "Problem Solving"
        ],
        "minimum_proficiency": "Beginner",
        "career_level": "Entry Level",
        "learning_roadmap": [
            {
                "step": 1,
                "topic": "HTML Fundamentals",
                "skills": ["HTML"],
                "duration": "1 week"
            },
            {
                "step": 2,
                "topic": "CSS and Responsive Design",
                "skills": ["CSS"],
                "duration": "2 weeks"
            },
            {
                "step": 3,
                "topic": "JavaScript",
                "skills": ["JavaScript"],
                "duration": "4 weeks"
            },
            {
                "step": 4,
                "topic": "React",
                "skills": ["React"],
                "duration": "3 weeks"
            },
            {
                "step": 5,
                "topic": "Build a Full Web Project",
                "skills": ["Problem Solving"],
                "duration": "3 weeks"
            }
        ]
    },

    {
        "career_id": 5,
        "career_name": "Data Engineer",
        "description": (
            "Builds and maintains data pipelines, data storage "
            "systems, and infrastructure for large-scale data processing."
        ),
        "required_skills": [
            "Python",
            "SQL",
            "ETL",
            "Data Pipelines",
            "Cloud Computing"
        ],
        "interests": [
            "Data Engineering",
            "Database Management",
            "Automation",
            "System Design",
            "Problem Solving"
        ],
        "minimum_proficiency": "Intermediate",
        "career_level": "Intermediate",
        "learning_roadmap": [
            {
                "step": 1,
                "topic": "Python Programming",
                "skills": ["Python"],
                "duration": "3 weeks"
            },
            {
                "step": 2,
                "topic": "SQL and Database Management",
                "skills": ["SQL"],
                "duration": "3 weeks"
            },
            {
                "step": 3,
                "topic": "ETL and Data Pipelines",
                "skills": ["ETL", "Data Pipelines"],
                "duration": "4 weeks"
            },
            {
                "step": 4,
                "topic": "Cloud Computing Fundamentals",
                "skills": ["Cloud Computing"],
                "duration": "3 weeks"
            },
            {
                "step": 5,
                "topic": "Build a Data Pipeline Project",
                "skills": ["Data Pipelines"],
                "duration": "3 weeks"
            }
        ]
    },

    {
        "career_id": 6,
        "career_name": "Machine Learning Engineer",
        "description": (
            "Develops, tests, and deploys machine learning models "
            "for practical applications."
        ),
        "required_skills": [
            "Python",
            "Machine Learning",
            "Statistics",
            "Data Processing",
            "Model Deployment"
        ],
        "interests": [
            "Artificial Intelligence",
            "Machine Learning",
            "Automation",
            "Mathematics",
            "Research"
        ],
        "minimum_proficiency": "Intermediate",
        "career_level": "Intermediate",
        "learning_roadmap": [
            {
                "step": 1,
                "topic": "Python and Data Processing",
                "skills": ["Python", "Data Processing"],
                "duration": "4 weeks"
            },
            {
                "step": 2,
                "topic": "Statistics and Probability",
                "skills": ["Statistics"],
                "duration": "3 weeks"
            },
            {
                "step": 3,
                "topic": "Machine Learning Algorithms",
                "skills": ["Machine Learning"],
                "duration": "5 weeks"
            },
            {
                "step": 4,
                "topic": "Model Deployment",
                "skills": ["Model Deployment"],
                "duration": "3 weeks"
            },
            {
                "step": 5,
                "topic": "End-to-End ML Project",
                "skills": ["Machine Learning", "Model Deployment"],
                "duration": "3 weeks"
            }
        ]
    },

    {
        "career_id": 7,
        "career_name": "Cybersecurity Analyst",
        "description": (
            "Monitors systems, identifies security vulnerabilities, "
            "and helps protect networks and information from threats."
        ),
        "required_skills": [
            "Networking",
            "Linux",
            "Cybersecurity",
            "Python",
            "Problem Solving"
        ],
        "interests": [
            "Cybersecurity",
            "Network Security",
            "Ethical Hacking",
            "Investigation",
            "Problem Solving"
        ],
        "minimum_proficiency": "Beginner",
        "career_level": "Entry Level",
        "learning_roadmap": [
            {
                "step": 1,
                "topic": "Computer Networking",
                "skills": ["Networking"],
                "duration": "3 weeks"
            },
            {
                "step": 2,
                "topic": "Linux Fundamentals",
                "skills": ["Linux"],
                "duration": "2 weeks"
            },
            {
                "step": 3,
                "topic": "Security Fundamentals",
                "skills": ["Cybersecurity"],
                "duration": "4 weeks"
            },
            {
                "step": 4,
                "topic": "Python for Security Automation",
                "skills": ["Python"],
                "duration": "3 weeks"
            },
            {
                "step": 5,
                "topic": "Security Lab Projects",
                "skills": ["Problem Solving"],
                "duration": "3 weeks"
            }
        ]
    },

    {
        "career_id": 8,
        "career_name": "Cloud Engineer",
        "description": (
            "Designs, deploys, and maintains cloud infrastructure "
            "and services for applications and organizations."
        ),
        "required_skills": [
            "Cloud Computing",
            "Linux",
            "Networking",
            "Python",
            "DevOps"
        ],
        "interests": [
            "Cloud Computing",
            "Infrastructure",
            "Automation",
            "System Design",
            "Problem Solving"
        ],
        "minimum_proficiency": "Intermediate",
        "career_level": "Intermediate",
        "learning_roadmap": [
            {
                "step": 1,
                "topic": "Linux Fundamentals",
                "skills": ["Linux"],
                "duration": "2 weeks"
            },
            {
                "step": 2,
                "topic": "Networking Fundamentals",
                "skills": ["Networking"],
                "duration": "3 weeks"
            },
            {
                "step": 3,
                "topic": "Cloud Computing",
                "skills": ["Cloud Computing"],
                "duration": "4 weeks"
            },
            {
                "step": 4,
                "topic": "Python and Automation",
                "skills": ["Python", "DevOps"],
                "duration": "4 weeks"
            },
            {
                "step": 5,
                "topic": "Deploy a Cloud Project",
                "skills": ["Cloud Computing"],
                "duration": "3 weeks"
            }
        ]
    }
]


def get_all_careers():
    """
    Return the complete career dataset.
    """
    return CAREER_DATASET


def get_career_by_id(career_id):
    """
    Find a career using its ID.
    """
    for career in CAREER_DATASET:
        if career["career_id"] == career_id:
            return career

    return None


def get_career_by_name(career_name):
    """
    Find a career using its name.
    """
    search_name = career_name.strip().lower()

    for career in CAREER_DATASET:
        if career["career_name"].lower() == search_name:
            return career

    return None


def get_all_skill_names():
    """
    Return all unique skills present in the dataset.
    """
    skills = set()

    for career in CAREER_DATASET:
        skills.update(career["required_skills"])

    return sorted(skills)


def get_all_interests():
    """
    Return all unique interests present in the dataset.
    """
    interests = set()

    for career in CAREER_DATASET:
        interests.update(career["interests"])

    return sorted(interests)


if __name__ == "__main__":
    print("=" * 55)
    print("AI CAREER NAVIGATOR - CAREER DATASET")
    print("=" * 55)

    print(f"\nTotal careers: {len(get_all_careers())}")
    print(f"Total unique skills: {len(get_all_skill_names())}")
    print(f"Total unique interests: {len(get_all_interests())}")

    print("\nAvailable Careers:")

    for career in get_all_careers():
        print(
            f'{career["career_id"]}. '
            f'{career["career_name"]}'
        )

    print("\nAvailable Skills:")
    print(", ".join(get_all_skill_names()))

    print("\nAvailable Interests:")
    print(", ".join(get_all_interests()))

    print("\nDataset loaded successfully!")
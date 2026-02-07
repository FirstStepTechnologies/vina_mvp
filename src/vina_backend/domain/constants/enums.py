"""
Application-wide enums and constants.
"""
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"


class ExperienceLevel(str, Enum):
    """User experience levels."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class TechnicalComfort(str, Enum):
    """Technical comfort levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Profession(str, Enum):
    """Supported professions."""
    CLINICAL_RESEARCHER = "Clinical Researcher"
    HR_MANAGER = "HR Manager"
    PROJECT_MANAGER = "Project Manager"
    MARKETING_MANAGER = "Marketing Manager"


# Profession options for the hackathon
SUPPORTED_PROFESSIONS = [
    "Clinical Researcher",
    "HR Manager",
    "Project Manager",
    "Marketing Manager",
]

# Industry options by profession
INDUSTRIES_BY_PROFESSION = {
    "Clinical Researcher": [
        "Pharma/Biotech",
        "Academic Research",
        "Contract Research Organisation (CRO)",
    ],
    "HR Manager": [
        "Tech Company",
        "Healthcare",
        "Financial Services",
    ],
    "Project Manager": [
        "Software/Tech",
        "Construction/Engineering",
        "Consulting",
    ],
    "Marketing Manager": [
        "E-Commerce",
        "SaaS",
        "Consumer Goods",
    ],
}
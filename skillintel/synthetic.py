"""Synthetic employee profiles for demos and tests. No real personal data is used."""

from __future__ import annotations

import random

ARCHETYPES: dict[str, list[str]] = {
    "ai": [
        "Built RAG pipelines with LangChain and an OpenAI API; NLP classification models",
        "Trained machine learning models with scikit-learn and tracked them with MLflow",
        "Prompt engineering for LLM assistants; deployed model services with FastAPI and Docker",
    ],
    "data": [
        "Maintained ETL data pipelines on Azure Data Factory and Azure Synapse using SQL",
        "Built PySpark jobs on Databricks and automated deployments with Azure DevOps",
        "Designed data engineering workflows in Python and SQL with Git-based review",
    ],
    "analytics": [
        "Created Power BI dashboards and Excel models; ran statistical analysis in SQL",
        "Presented insights to stakeholders; communication and presentation skills",
        "Hypothesis testing and reporting with Excel, SQL and Power BI",
    ],
    "web": [
        "Built React and TypeScript front ends with HTML/CSS; REST API integration",
        "Node.js services, JavaScript tooling, unit testing with pytest",
        "Full-stack work: React, JavaScript, REST APIs and CI/CD with GitHub Actions",
    ],
    "management": [
        "Led a team of eight; agile sprint planning in Jira; stakeholder management",
        "Project management, mentoring and line management across delivery squads",
        "Client communication, scrum ceremonies and people management",
    ],
}


def generate_profiles(n: int = 60, seed: int = 7) -> dict[str, str]:
    """Return ``{employee_ref: free-text profile}`` with a mix of archetypes and some noise."""
    rng = random.Random(seed)
    names = list(ARCHETYPES)
    profiles = {}
    for i in range(n):
        primary = names[i % len(names)]
        parts = rng.sample(ARCHETYPES[primary], k=2)
        if rng.random() < 0.3:  # cross-skilled employees
            other = rng.choice([x for x in names if x != primary])
            parts.append(rng.choice(ARCHETYPES[other]))
        if rng.random() < 0.5:
            parts.append("Version control with Git and GitHub")
        profiles[f"HR-{1000 + i}"] = ". ".join(parts) + "."
    return profiles

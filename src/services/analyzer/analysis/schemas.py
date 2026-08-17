from typing import Literal, final

from services.api.common.schemas import CamelCaseModel

Status = Literal["positive", "neutral", "attention", "negative", "unknown"]
Severity = Literal["info", "low", "medium", "high", "critical"]
EvidenceLevel = Literal[
    "not_found",
    "claimed_only",
    "project_context",
    "concrete_application",
    "complex_task",
    "measurable_result",
]
EstimatedLevel = Literal[
    "intern",
    "junior",
    "junior_plus",
    "middle_minus",
    "middle",
    "middle_plus",
    "senior",
    "lead",
    "unknown",
]
EstimatedDepth = Literal[
    "basic", "intermediate", "advanced", "expert", "unknown"
]
# Analyst profile keys; rendered to Russian labels in code (PROFILE_LABELS).
MainProfile = Literal[
    "system_analyst",
    "business_analyst",
    "product_analyst",
    "data_analyst",
    "bi_analyst",
]
# The company's industry sector, classified by the model from general
# knowledge of the employer (a factual classification, not a reputation
# judgement). Which sectors count as a bonus domain is configured in code.
Sector = Literal[
    "banking",
    "fintech",
    "insurance",
    "investment",
    "telecom",
    "retail",
    "ecommerce",
    "it_services",
    "media",
    "gamedev",
    "transport",
    "manufacturing",
    "energy",
    "healthcare",
    "government",
    "education",
    "other",
    "unknown",
]


@final
class AnalysisMetadata(CamelCaseModel):
    """Reproducible metadata owned by the application, not the model."""

    id: str
    status: Literal["pending", "processing", "completed", "failed", "partial"]
    created_at: str
    model: str | None


@final
class Candidate(CamelCaseModel):
    """The minimal candidate identity shown on the report."""

    full_name: str | None
    current_title: str | None
    age: int | None = None
    salary_value: int | None = None
    salary_currency: str | None = None
    resume_updated_date: str | None = None


@final
class Highlight(CamelCaseModel):
    """One punchy, standalone takeaway about the candidate.

    Rendered as a colour-coded bullet in the report: ``status`` marks it as a
    strength, a neutral fact, or something to watch — the same traffic-light
    language used across the dashboard.
    """

    text: str
    status: Status


@final
class Summary(CamelCaseModel):
    """The headline verdict of the analysis."""

    headline: str
    highlights: list[Highlight]
    main_profile: MainProfile
    estimated_level: EstimatedLevel


@final
class EmploymentGap(CamelCaseModel):
    """A gap between two employments (dates come from computed facts)."""

    start_date: str | None
    end_date: str | None
    duration_months: int


@final
class ExperienceSummary(CamelCaseModel):
    """Aggregated chronology; totals and gaps come from computed facts."""

    total_months: int | None
    gaps: list[EmploymentGap]


@final
class ExperienceAssessment(CamelCaseModel):
    """A per-place-of-work assessment (dates come from computed facts)."""

    id: str
    company: str
    role: str | None = None
    start_date: str | None
    end_date: str | None
    duration_months: int | None
    status: Status
    responsibilities: str | None = None


@final
class SkillAssessment(CamelCaseModel):
    """An assessment of a single skill's depth and evidence."""

    id: str
    name: str
    group: str
    evidence_level: EvidenceLevel
    estimated_depth: EstimatedDepth
    contexts: list[str]
    experience_ids: list[str]


@final
class CompanyAssessment(CamelCaseModel):
    """An assessment of one employer as a signal."""

    experience_id: str
    sector: Sector = "unknown"
    signal: Status


@final
class EducationItem(CamelCaseModel):
    """A single education record."""

    kind: Literal["degree", "course"] = "degree"
    institution: str
    faculty: str | None
    speciality: str | None
    year: int | None
    technical: bool | None


@final
class Risk(CamelCaseModel):
    """A risk raised by the analysis."""

    title: str
    severity: Severity
    explanation: str


@final
class Unknown(CamelCaseModel):
    """A missing fact that should be clarified."""

    subject: str
    reason: str


@final
class ScreeningQuestion(CamelCaseModel):
    """A question to ask the candidate during screening."""

    question: str
    reason: str
    priority: Severity


@final
class ResumeAnalysis(CamelCaseModel):
    """Structured analysis result; chronology is overwritten in code."""

    schema_version: Literal["2.0.0"]
    analysis: AnalysisMetadata
    candidate: Candidate
    summary: Summary
    experience_summary: ExperienceSummary
    experiences: list[ExperienceAssessment]
    skills: list[SkillAssessment]
    company_assessments: list[CompanyAssessment]
    education_items: list[EducationItem]
    risks: list[Risk]
    unknowns: list[Unknown]
    screening_questions: list[ScreeningQuestion]

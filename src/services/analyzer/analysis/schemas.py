from typing import Literal, final

from services.analyzer.analysis.choices import (
    EducationKind,
    EstimatedDepth,
    EstimatedLevel,
    EvidenceLevel,
    MainProfile,
    MetadataStatus,
    RoleRelevance,
    Sector,
    Severity,
    Status,
)
from services.api.common.schemas import CamelCaseModel


@final
class AnalysisMetadata(CamelCaseModel):
    """Reproducible metadata owned by the application, not the model."""

    id: str
    status: MetadataStatus
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
    """One standalone, traffic-light-coloured takeaway about the candidate."""

    text: str
    status: Status


@final
class Summary(CamelCaseModel):
    """The headline verdict of the analysis."""

    headline: str
    highlights: list[Highlight]
    main_profile: MainProfile
    estimated_level: EstimatedLevel
    role_fit: int


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
    relevance: RoleRelevance
    responsibilities: str | None = None


@final
class SkillAssessment(CamelCaseModel):
    """An assessment of a single skill's depth and evidence."""

    id: str
    name: str
    group: str
    core: bool
    evidence_level: EvidenceLevel
    estimated_depth: EstimatedDepth
    contexts: list[str]
    experience_ids: list[str]


@final
class CompanyAssessment(CamelCaseModel):
    """An assessment of one employer as a signal."""

    experience_id: str
    sector: Sector = Sector.UNKNOWN
    signal: Status


@final
class EducationItem(CamelCaseModel):
    """A single education record."""

    kind: EducationKind = EducationKind.DEGREE
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

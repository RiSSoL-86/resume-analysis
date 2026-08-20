from typing import final

from services.api.common.schemas import CamelCaseModel


@final
class CareerFactExperience(CamelCaseModel):
    """One deterministically computed place of work."""

    source_experience_id: str | None
    company: str | None
    role: str | None
    start_date: str
    end_date: str
    is_current: bool
    duration_months: int
    is_shorter_than_12_months: bool
    transition_reason: str | None
    responsibilities: str | None


@final
class CandidateSalary(CamelCaseModel):
    """The candidate's stated salary expectation, read from the resume."""

    value: int
    currency: str


@final
class CareerFactGap(CamelCaseModel):
    """A deterministically computed gap between two jobs."""

    after_company: str | None
    before_company: str | None
    start_date: str
    end_date: str
    duration_months: int


@final
class CareerFacts(CamelCaseModel):
    """Chronology computed in code; the model must not recalculate it."""

    authority: str
    master_resume_id: str | None
    age: int | None
    salary: CandidateSalary | None
    resume_updated_date: str | None
    experiences: list[CareerFactExperience]
    total_months: int
    jobs_count: int
    average_job_months: float | None
    short_jobs_count: int
    gaps: list[CareerFactGap]
    instruction: str

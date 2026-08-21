from typing import Literal, NamedTuple, final

from services.analyzer.analysis.choices import Status
from services.analyzer.analysis.schemas import (
    Candidate,
    Unknown,
)
from services.api.common.schemas import CamelCaseModel


class LifeInterval(NamedTuple):
    """Internal builder span (months since year 0), before positioning."""

    start: int
    end: int
    kind: Literal["education", "course", "job", "gap"]
    label: str
    status: Status
    hint: str
    role: str = ""
    responsibilities: str = ""


@final
class DashboardHero(CamelCaseModel):
    """The headline block shown at the top of the report."""

    full_name: str | None
    initials: str
    headline: str
    age_label: str
    salary_label: str
    updated_label: str | None
    updated_status: Status
    main_profile: str
    level: str
    level_status: Status
    experience_status: Status
    overall_score: int
    overall_status: Status


@final
class DashboardSkill(CamelCaseModel):
    """A skill scored for the skills grid."""

    name: str
    group: str
    score: int
    status: Status


@final
class DashboardDetail(CamelCaseModel):
    """One responsibilities line; ``head`` marks a subheading, not a bullet."""

    text: str
    head: bool = False


@final
class DashboardTimelineBlock(CamelCaseModel):
    """One life-timeline card; ``top``/``height`` are its packed pixel slot."""

    title: str
    subtitle: str
    role: str = ""
    duration: str = ""
    period: str
    status: Status
    kind: Literal["job", "education", "course", "gap"]
    current: bool = False
    logo: str = ""
    logo_svg: str = ""
    details: list[DashboardDetail] = []
    top: float
    height: float


@final
class DashboardTimelineYear(CamelCaseModel):
    """A year tick along the vertical timeline axis (pixels from the top)."""

    label: str
    position: float
    current: bool


@final
class DashboardDomain(CamelCaseModel):
    """Bonus domain experience (e.g. banking) for the target profile."""

    label: str
    value: str
    status: Status


@final
class DashboardRisk(CamelCaseModel):
    """A risk prepared for rendering with a traffic-light status."""

    title: str
    status: Status
    explanation: str


@final
class DashboardQuestion(CamelCaseModel):
    """A screening question prepared for rendering with a status."""

    question: str
    reason: str
    status: Status


@final
class DashboardEducationItem(CamelCaseModel):
    """One education record prepared for rendering."""

    institution: str
    speciality: str | None
    year: int | None
    status: Status


@final
class DashboardHighlight(CamelCaseModel):
    """One colour-coded takeaway bullet for the summary block."""

    text: str
    status: Status


@final
class DashboardEducation(CamelCaseModel):
    """The education block prepared for rendering."""

    items: list[DashboardEducationItem]


@final
class Dashboard(CamelCaseModel):
    """The complete presentation model for a resume analysis."""

    candidate: Candidate
    hero: DashboardHero
    highlights: list[DashboardHighlight] = []
    featured_skills: list[DashboardSkill]
    other_skills: list[DashboardSkill]
    timeline_total_label: str
    lifeline_work: list[DashboardTimelineBlock] = []
    lifeline_gaps: list[DashboardTimelineBlock] = []
    lifeline_study: list[DashboardTimelineBlock] = []
    lifeline_years: list[DashboardTimelineYear] = []
    lifeline_height: int = 0
    domain: DashboardDomain
    gaps_status: Status
    gaps_label: str
    risks: list[DashboardRisk]
    unknowns: list[Unknown]
    questions: list[DashboardQuestion]
    education: DashboardEducation

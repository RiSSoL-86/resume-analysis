import html
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, final, override

from apps.common.services.base import BaseService
from services.analyzer.analysis.choices import RoleRelevance, Sector, Status
from services.analyzer.dashboard.constants import (
    COURSE_DEFAULT_MONTHS,
    GAP_ATTENTION_MONTHS,
    LEVEL_LABELS,
    PRIORITY_DOMAIN_LABEL,
    PRIORITY_DOMAIN_SECTORS,
    PROFILE_LABELS,
    RELEVANCE_WEIGHTS,
    SECTOR_LABELS,
    SEVERITY_ORDER,
    STUDY_DEFAULT_MONTHS,
)
from services.analyzer.dashboard.constants.geometry import (
    AXIS_MIN_HEIGHT,
    CARD_GAP,
    COMPRESS_RELAX,
    LINEAR_MONTHS,
    MIN_HEIGHTS,
    MONTH_STEP,
    YEAR_LABEL_GAP,
)
from services.analyzer.dashboard.constants.logos import COMPANY_LOGOS
from services.analyzer.dashboard.schemas import (
    Dashboard,
    DashboardDetail,
    DashboardDomain,
    DashboardEducation,
    DashboardEducationItem,
    DashboardHero,
    DashboardHighlight,
    DashboardQuestion,
    DashboardRisk,
    DashboardSkill,
    DashboardTimelineBlock,
    DashboardTimelineYear,
    LifeInterval,
)
from services.analyzer.dashboard.utils import (
    age_label,
    compact_text,
    depth_level,
    duration_label,
    education_item_status,
    experience_status,
    gaps_label,
    gaps_overall_status,
    level_status,
    month_year_label,
    overall_score,
    overall_status,
    prune_covered_unknowns,
    salary_label,
    severity_status,
    skill_score,
    skill_status,
    tenure_status,
    updated_label,
    updated_status,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from services.analyzer.analysis.schemas import (
        CompanyAssessment,
        ResumeAnalysis,
        SkillAssessment,
    )


@final
class DashboardBuilderService(BaseService):
    """Project a structured analysis into the presentation model."""

    RESP_SPLIT: Final = re.compile(r"<br\s*/?>|</?p\s*/?>", re.IGNORECASE)
    RESP_TAG: Final = re.compile(r"<[^>]+>")
    RESP_BULLET: Final = re.compile(r"^[-–•·*]+")

    @override
    async def execute(self, analysis: ResumeAnalysis) -> Dashboard:
        """Build the dashboard view model from the analysis."""
        featured, other = self.build_skills(analysis)
        domain = self.build_domain(analysis)
        gap_months = self._gap_months(analysis)
        (
            lifeline_work,
            lifeline_gaps,
            lifeline_study,
            lifeline_years,
            lifeline_height,
        ) = self.build_lifeline(analysis)
        return Dashboard(
            candidate=analysis.candidate,
            hero=self.build_hero(analysis, featured, domain, gap_months),
            highlights=self.build_highlights(analysis),
            featured_skills=featured,
            other_skills=other,
            timeline_total_label=duration_label(
                analysis.experience_summary.total_months
            ),
            lifeline_work=lifeline_work,
            lifeline_gaps=lifeline_gaps,
            lifeline_study=lifeline_study,
            lifeline_years=lifeline_years,
            lifeline_height=lifeline_height,
            domain=domain,
            gaps_status=gaps_overall_status(gap_months),
            gaps_label=gaps_label(gap_months),
            risks=self.build_risks(analysis),
            unknowns=prune_covered_unknowns(analysis.unknowns, analysis.risks)[
                :2
            ],
            questions=self.build_questions(analysis),
            education=self.build_education(analysis),
        )

    @staticmethod
    def _tenure(analysis: ResumeAnalysis) -> dict[str, int]:
        """Map each experience id to its duration in months."""
        return {
            item.id: (item.duration_months or 0)
            for item in analysis.experiences
        }

    @staticmethod
    def _relevant_months(analysis: ResumeAnalysis) -> int:
        """Total tenure weighted by each job's relevance to the target role."""
        return round(
            sum(
                (item.duration_months or 0) * RELEVANCE_WEIGHTS[item.relevance]
                for item in analysis.experiences
            )
        )

    @classmethod
    def build_skills(
        cls, analysis: ResumeAnalysis
    ) -> tuple[list[DashboardSkill], list[DashboardSkill]]:
        """Split scored skills into model-flagged role-core and the rest."""
        tenure = cls._tenure(analysis)
        featured: list[DashboardSkill] = []
        other: list[DashboardSkill] = []
        for item in analysis.skills:
            bucket = featured if item.core else other
            bucket.append(cls._score_skill(item, tenure))
        featured.sort(key=lambda skill: (-skill.score, skill.name))
        other.sort(key=lambda skill: (-skill.score, skill.name))
        return featured, other

    @staticmethod
    def build_highlights(
        analysis: ResumeAnalysis,
    ) -> list[DashboardHighlight]:
        """The five colour-coded takeaway bullets authored by the model."""
        return [
            DashboardHighlight(text=item.text, status=item.status)
            for item in analysis.summary.highlights
            if item.text.strip()
        ]

    @staticmethod
    def _score_skill(
        item: SkillAssessment, tenure: dict[str, int]
    ) -> DashboardSkill:
        """Score one skill from its mentions, tenure and depth."""
        depth = depth_level(item.estimated_depth)
        mentions = len(item.contexts) or len(item.experience_ids)
        months = sum(tenure.get(eid, 0) for eid in item.experience_ids)
        score = skill_score(mentions, months, depth)
        return DashboardSkill(
            name=item.name,
            group=item.group,
            score=score,
            status=skill_status(score),
        )

    @classmethod
    def _gap_months(cls, analysis: ResumeAnalysis) -> list[int]:
        """Notable gap durations, longest first, plus trailing idle."""
        gaps = [
            gap.duration_months
            for gap in analysis.experience_summary.gaps
            if gap.duration_months >= GAP_ATTENTION_MONTHS
        ]
        trailing = cls._trailing_gap_months(analysis)
        if trailing >= GAP_ATTENTION_MONTHS:
            gaps.append(trailing)
        return sorted(gaps, reverse=True)

    @classmethod
    def _trailing_gap_months(cls, analysis: ResumeAnalysis) -> int:
        """Months between the last job's end and today (0 if still working)."""
        finishes = [
            month
            for job in analysis.experiences
            if (month := cls._month_index(job.end_date)) is not None
        ]
        if not finishes:
            return 0
        return max(0, cls._current_month() - max(finishes))

    @staticmethod
    def build_questions(
        analysis: ResumeAnalysis,
    ) -> list[DashboardQuestion]:
        """Keep the few highest-priority screening questions, coloured."""
        ordered = sorted(
            analysis.screening_questions,
            key=lambda item: SEVERITY_ORDER.index(item.priority),
        )
        return [
            DashboardQuestion(
                question=item.question,
                reason=item.reason,
                status=severity_status(item.priority),
            )
            for item in ordered[:4]
        ]

    @classmethod
    def build_hero(
        cls,
        analysis: ResumeAnalysis,
        featured: list[DashboardSkill],
        domain: DashboardDomain,
        gap_months: list[int],
    ) -> DashboardHero:
        """Build the headline block with the overall candidate rating."""
        summary = analysis.summary
        score = overall_score(
            skill_scores=[skill.score for skill in featured],
            level=summary.estimated_level,
            role_fit=summary.role_fit,
            relevant_months=cls._relevant_months(analysis),
            domain_present=domain.status == Status.POSITIVE,
            job_tenures=list(cls._tenure(analysis).values()),
            gap_months=gap_months,
        )
        candidate = analysis.candidate
        return DashboardHero(
            full_name=candidate.full_name,
            initials=cls._initials(candidate.full_name),
            headline=summary.headline,
            age_label=age_label(candidate.age),
            salary_label=salary_label(
                candidate.salary_value, candidate.salary_currency
            ),
            updated_label=updated_label(candidate.resume_updated_date),
            updated_status=updated_status(candidate.resume_updated_date),
            main_profile=PROFILE_LABELS.get(
                summary.main_profile, summary.main_profile
            ),
            level=LEVEL_LABELS[summary.estimated_level],
            level_status=level_status(summary.estimated_level),
            experience_status=experience_status(
                analysis.experience_summary.total_months
            ),
            overall_score=score,
            overall_status=overall_status(score),
        )

    @staticmethod
    def _initials(full_name: str | None) -> str:
        """Up to two uppercase initials from a name, for the avatar."""
        parts = [word for word in (full_name or "").split() if word]
        letters = [word[0].upper() for word in parts[:2]]
        return "".join(letters) or "?"

    @classmethod
    def build_lifeline(
        cls, analysis: ResumeAnalysis
    ) -> tuple[
        list[DashboardTimelineBlock],
        list[DashboardTimelineBlock],
        list[DashboardTimelineBlock],
        list[DashboardTimelineYear],
        int,
    ]:
        """Lay work, study and breaks on one compressed-past vertical axis."""
        now = cls._current_month()
        work = cls._work_intervals(analysis)
        study = cls._study_intervals(analysis)
        gaps = cls._gap_intervals(analysis, now)
        if not work and not study:
            return [], [], [], [], 0
        spans = work + study + gaps
        axis_start = (min(item.start for item in spans) // 12) * 12

        def pos(month: int) -> float:
            months_ago = max(now - month, 0)
            if months_ago <= LINEAR_MONTHS:
                return MONTH_STEP * months_ago
            tail = months_ago - LINEAR_MONTHS
            compressed = (
                MONTH_STEP * COMPRESS_RELAX * tail / (tail + COMPRESS_RELAX)
            )
            return MONTH_STEP * LINEAR_MONTHS + compressed

        work_blocks, work_bottom = cls._place_column(work, now, pos)
        side_blocks, side_bottom = cls._place_column(study + gaps, now, pos)
        study_blocks = [b for b in side_blocks if b.kind != "gap"]
        gap_blocks = [b for b in side_blocks if b.kind == "gap"]
        years = cls._timeline_years(axis_start, now, pos)
        deepest_tick = max((y.position for y in years), default=0.0)
        height = (
            int(
                max(
                    AXIS_MIN_HEIGHT,
                    work_bottom,
                    side_bottom,
                    deepest_tick + 14,
                )
            )
            + 8
        )
        return work_blocks, gap_blocks, study_blocks, years, height

    @classmethod
    def _place_column(
        cls,
        intervals: list[LifeInterval],
        now: int,
        pos: Callable[[int], float],
    ) -> tuple[list[DashboardTimelineBlock], float]:
        """Place each card as its span, flooring shorts, packing overlaps."""
        blocks: list[DashboardTimelineBlock] = []
        cursor = 0.0
        for item in sorted(intervals, key=lambda entry: -entry.end):
            axis_top = pos(item.end)
            axis_bottom = pos(item.start)
            height = max(axis_bottom - axis_top, MIN_HEIGHTS[item.kind])
            top = max(axis_top, cursor)
            cursor = top + height + CARD_GAP
            blocks.append(
                DashboardTimelineBlock(
                    title=item.label,
                    subtitle=item.hint,
                    role=item.role,
                    duration=(
                        cls._compact_months(item.end - item.start)
                        if item.kind == "job"
                        else ""
                    ),
                    period=cls._period_label(item, now),
                    status=item.status,
                    kind=item.kind,
                    current=item.kind == "job" and item.end >= now,
                    logo=cls._card_badge(item),
                    logo_svg=cls._card_logo_svg(item),
                    details=cls._responsibility_details(item.responsibilities),
                    top=round(top, 1),
                    height=round(height, 1),
                )
            )
        return blocks, cursor

    @classmethod
    def _responsibility_details(cls, raw: str) -> list[DashboardDetail]:
        """Clean the resume responsibilities HTML into bullet/heading lines."""
        details: list[DashboardDetail] = []
        for chunk in cls.RESP_SPLIT.split(raw or ""):
            text = html.unescape(cls.RESP_TAG.sub("", chunk)).replace(
                "\t", " "
            )
            text = text.strip()
            bullet = bool(cls.RESP_BULLET.match(text))
            text = " ".join(cls.RESP_BULLET.sub("", text).split())
            if not text:
                continue
            head = not bullet and text.endswith(":")
            details.append(DashboardDetail(text=text, head=head))
        return details

    @staticmethod
    def _card_badge(item: LifeInterval) -> str:
        """Fallback glyph when a card has no real logo: company initials."""
        if item.kind == "job":
            return DashboardBuilderService._initials(item.label)
        return ""

    @staticmethod
    def _card_logo_svg(item: LifeInterval) -> str:
        """A built-in brand badge (inline SVG) if the employer is known."""
        if item.kind != "job":
            return ""
        name = item.label.casefold()
        for keyword, svg in COMPANY_LOGOS.items():
            if keyword in name:
                return svg
        return ""

    @classmethod
    def _period_label(cls, item: LifeInterval, now: int) -> str:
        """Human date range for a card; study shows only its known year."""
        if item.kind == "gap":
            return ""
        if item.kind == "job":
            start = month_year_label(item.start)
            end = (
                "настоящее время"
                if item.end >= now
                else month_year_label(item.end)
            )
            return f"{start} — {end}"
        year = item.end // 12
        return str(year) if item.kind == "course" else f"выпуск {year}"

    @classmethod
    def _gap_intervals(
        cls, analysis: ResumeAnalysis, now: int
    ) -> list[LifeInterval]:
        """Red break markers between jobs, plus the trailing idle stretch."""
        intervals: list[LifeInterval] = []
        finishes = [
            month
            for job in analysis.experiences
            if (month := cls._month_index(job.end_date)) is not None
        ]
        last_end = max(finishes) if finishes else None
        for gap in analysis.experience_summary.gaps:
            if gap.duration_months < GAP_ATTENTION_MONTHS:
                continue  # trivial month-or-two breaks add only clutter
            begin = cls._month_index(gap.start_date)
            finish = cls._month_index(gap.end_date)
            if begin is None or finish is None or finish <= begin:
                continue
            if last_end is not None and begin >= last_end:
                continue  # part of the trailing idle stretch, drawn below
            intervals.append(
                LifeInterval(
                    start=begin,
                    end=finish,
                    kind="gap",
                    label="Перерыв в карьере",
                    status=Status.NEGATIVE,
                    hint=cls._compact_months(gap.duration_months),
                )
            )
        trailing = cls._trailing_gap_months(analysis)
        if trailing >= GAP_ATTENTION_MONTHS:
            intervals.append(
                LifeInterval(
                    start=now - trailing,
                    end=now,
                    kind="gap",
                    label="Перерыв в карьере",
                    status=Status.NEGATIVE,
                    hint=cls._compact_months(trailing),
                )
            )
        return intervals

    @staticmethod
    def _compact_months(months: int) -> str:
        """Very short break label like ``3м`` or ``1г 2м`` for a gap box."""
        if months < 12:
            return f"{months}м"
        years, rest = divmod(months, 12)
        return f"{years}г" if not rest else f"{years}г {rest}м"

    @staticmethod
    def _timeline_years(
        axis_start: int, now: int, pos: Callable[[int], float]
    ) -> list[DashboardTimelineYear]:
        """Year ticks down the axis, thinned; oldest year is always kept."""
        oldest = axis_start // 12
        years: list[DashboardTimelineYear] = [
            DashboardTimelineYear(label="сейчас", position=0.0, current=True)
        ]
        for year in range(now // 12, oldest - 1, -1):
            position = round(pos(year * 12), 1)
            if year == oldest:
                while len(years) > 1 and position - years[-1].position < (
                    YEAR_LABEL_GAP
                ):
                    years.pop()
            elif position - years[-1].position < YEAR_LABEL_GAP:
                continue
            years.append(
                DashboardTimelineYear(
                    label=str(year), position=position, current=False
                )
            )
        return years

    @classmethod
    def _study_intervals(cls, analysis: ResumeAnalysis) -> list[LifeInterval]:
        """Dated degrees (clamped to not overlap) and point-event courses."""
        intervals: list[LifeInterval] = []
        degrees = sorted(
            (
                item
                for item in analysis.education_items
                if item.kind != "course"
            ),
            key=lambda item: item.year or 0,
        )
        prev_end: int | None = None
        for item in degrees:
            if not item.year:
                continue
            anchor = item.year * 12 + 6
            start = anchor - STUDY_DEFAULT_MONTHS
            if prev_end is not None and start < prev_end:
                start = prev_end
            prev_end = anchor
            intervals.append(
                LifeInterval(
                    start=start,
                    end=anchor,
                    kind="education",
                    label=item.institution,
                    status=education_item_status(item.technical),
                    hint=item.speciality or item.faculty or "Образование",
                )
            )
        for item in analysis.education_items:
            if not item.year or item.kind != "course":
                continue
            anchor = item.year * 12 + 6
            intervals.append(
                LifeInterval(
                    start=anchor - COURSE_DEFAULT_MONTHS,
                    end=anchor,
                    kind="course",
                    label=item.institution or item.speciality or "Курс",
                    status=Status.POSITIVE,
                    hint=item.speciality or "Курс",
                )
            )
        return intervals

    @classmethod
    def _work_intervals(cls, analysis: ResumeAnalysis) -> list[LifeInterval]:
        """Dated job intervals in months-since-year-0."""
        sectors = {
            company.experience_id: company.sector
            for company in analysis.company_assessments
        }
        intervals: list[LifeInterval] = []
        for job in analysis.experiences:
            begin = cls._month_index(job.start_date)
            finish = cls._month_index(job.end_date)
            if begin is None or finish is None or finish <= begin:
                continue
            months = job.duration_months or (finish - begin)
            sector = sectors.get(job.id, Sector.UNKNOWN)
            intervals.append(
                LifeInterval(
                    start=begin,
                    end=finish,
                    kind="job",
                    label=job.company,
                    status=tenure_status(months),
                    hint=SECTOR_LABELS[sector],
                    role=(job.role or "").strip(),
                    responsibilities=(job.responsibilities or "").strip(),
                )
            )
        return intervals

    @staticmethod
    def _month_index(date: str | None) -> int | None:
        """Months-since-year-0 for a ``YYYY-MM`` date, or None."""
        if not date or len(date) < 7:
            return None
        year, month = date[:4], date[5:7]
        if not (year.isdigit() and month.isdigit()):
            return None
        return int(year) * 12 + (int(month) - 1)

    @staticmethod
    def _current_month() -> int:
        """Months-since-year-0 for the current month."""
        today = datetime.now(UTC)
        return today.year * 12 + (today.month - 1)

    @classmethod
    def build_domain(cls, analysis: ResumeAnalysis) -> DashboardDomain:
        """Sum time spent in role-relevant bonus domains (banking/fintech)."""
        tenure = cls._tenure(analysis)
        relevance = {item.id: item.relevance for item in analysis.experiences}
        months = sum(
            tenure.get(company.experience_id, 0)
            for company in analysis.company_assessments
            if cls._is_priority_domain(company)
            and relevance.get(company.experience_id)
            is not RoleRelevance.UNRELATED
        )
        present = months > 0
        return DashboardDomain(
            label=PRIORITY_DOMAIN_LABEL,
            value=duration_label(months) if present else "Не найден",
            status=Status.POSITIVE if present else Status.NEUTRAL,
        )

    @staticmethod
    def _is_priority_domain(company: CompanyAssessment) -> bool:
        """Tell whether a company sits in a bonus domain by its sector."""
        return company.sector in PRIORITY_DOMAIN_SECTORS

    @staticmethod
    def build_risks(analysis: ResumeAnalysis) -> list[DashboardRisk]:
        """Order risks by severity and attach a traffic-light status."""
        ordered = sorted(
            analysis.risks,
            key=lambda item: SEVERITY_ORDER.index(item.severity),
        )
        return [
            DashboardRisk(
                title=item.title,
                status=severity_status(item.severity),
                explanation=compact_text(item.explanation, limit=220),
            )
            for item in ordered[:3]
        ]

    @staticmethod
    def build_education(analysis: ResumeAnalysis) -> DashboardEducation:
        """Prepare the education block with per-item traffic-light status."""
        return DashboardEducation(
            items=[
                DashboardEducationItem(
                    institution=item.institution,
                    speciality=item.speciality or item.faculty,
                    year=item.year,
                    status=education_item_status(item.technical),
                )
                for item in analysis.education_items
            ],
        )

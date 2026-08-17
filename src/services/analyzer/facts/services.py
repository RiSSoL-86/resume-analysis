from datetime import UTC, datetime
from typing import Any, final, override

from apps.common.services.base import BaseService
from services.analyzer.facts.utils import month_date, month_index
from services.analyzer.schemas import (
    CandidateSalary,
    CareerFactExperience,
    CareerFactGap,
    CareerFacts,
)

# hh.ru currency ids for the flat resume.salary form; the nested
# document.salary already carries a currency code, so this is only a fallback.
CURRENCY_BY_ID: dict[int, str] = {1: "RUB", 2: "USD", 3: "EUR"}


@final
class CareerFactsService(BaseService):
    """Compute the candidate's chronology once, deterministically."""

    COPY_INSTRUCTION = (
        "Copy these chronology values exactly; "
        "do not recalculate or replace them."
    )

    @override
    async def execute(self, dossier: dict[str, Any]) -> CareerFacts:
        """Build authoritative chronology facts from the dossier."""
        candidate = dossier.get("candidate", {})
        master_resume_id = str(candidate.get("masterResumeId") or "")
        work_experiences = dossier.get("resume_related", {}).get(
            "work_experiences", []
        )
        rows = [
            row
            for row in work_experiences
            if str(row.get("resumeId") or "") == master_resume_id
            and isinstance(row.get("fromDateObject"), dict)
        ]

        today = datetime.now(UTC)
        current_month = {"year": today.year, "month": today.month}
        experiences = [
            self.build_experience(row, current_month) for row in rows
        ]
        experiences.sort(key=lambda item: item.start_date)

        gaps = self.build_gaps(experiences)
        durations = [item.duration_months for item in experiences]
        return CareerFacts(
            authority="application_calculation",
            master_resume_id=master_resume_id or None,
            age=self.candidate_age(dossier, master_resume_id, today),
            salary=self.candidate_salary(dossier, master_resume_id),
            resume_updated_date=self.resume_updated_date(dossier),
            experiences=experiences,
            total_months=sum(durations),
            jobs_count=len(experiences),
            average_job_months=(
                round(sum(durations) / len(durations), 2)
                if durations
                else None
            ),
            short_jobs_count=sum(duration < 12 for duration in durations),
            gaps=gaps,
            instruction=self.COPY_INSTRUCTION,
        )

    @classmethod
    def candidate_age(
        cls,
        dossier: dict[str, Any],
        master_resume_id: str,
        today: datetime,
    ) -> int | None:
        """Resolve age from resumes (master first): field or birthday."""
        resumes = dossier.get("resumes") or []
        ordered = sorted(
            (r for r in resumes if isinstance(r, dict)),
            key=lambda r: str(r.get("id") or "") != master_resume_id,
        )
        for resume in ordered:
            sources = (resume, resume.get("document") or {})
            for source in sources:
                age = source.get("age")
                if isinstance(age, int) and 0 < age < 120:
                    return age
                derived = cls._age_from_birthday(
                    source.get("birthdayDateObject"), today
                )
                if derived is not None:
                    return derived
        return None

    @staticmethod
    def _age_from_birthday(birthday: Any, today: datetime) -> int | None:
        """Compute whole years from a ``{year, month, day}`` birthday."""
        if not isinstance(birthday, dict):
            return None
        year, month, day = (
            birthday.get("year"),
            birthday.get("month") or 1,
            birthday.get("day") or 1,
        )
        if not isinstance(year, int):
            return None
        had_birthday = (today.month, today.day) >= (month, day)
        age = today.year - year - (0 if had_birthday else 1)
        return age if 0 < age < 120 else None

    @classmethod
    def candidate_salary(
        cls, dossier: dict[str, Any], master_resume_id: str
    ) -> CandidateSalary | None:
        """Read the salary expectation from resumes (master first)."""
        resumes = dossier.get("resumes") or []
        ordered = sorted(
            (r for r in resumes if isinstance(r, dict)),
            key=lambda r: str(r.get("id") or "") != master_resume_id,
        )
        for resume in ordered:
            salary = cls._salary_from_resume(resume)
            if salary is not None:
                return salary
        return None

    @classmethod
    def _salary_from_resume(
        cls, resume: dict[str, Any]
    ) -> CandidateSalary | None:
        """Read salary from the nested document form, then the flat form."""
        document = resume.get("document") or {}
        nested = document.get("salary")
        if isinstance(nested, dict):
            value = cls._positive_int(nested.get("value"))
            if value is not None:
                currency = str(nested.get("currency") or "")
                return CandidateSalary(value=value, currency=currency)
        value = cls._positive_int(resume.get("salary"))
        if value is not None:
            currency_id = resume.get("currencyId")
            currency = (
                CURRENCY_BY_ID.get(currency_id, "")
                if isinstance(currency_id, int)
                else ""
            )
            return CandidateSalary(value=value, currency=currency)
        return None

    @staticmethod
    def _positive_int(value: Any) -> int | None:
        """Coerce a positive number to int, rejecting bools and junk."""
        if isinstance(value, bool) or not isinstance(value, int | float):
            return None
        return int(value) if value > 0 else None

    @staticmethod
    def resume_updated_date(dossier: dict[str, Any]) -> str | None:
        """The date the resume was last updated at the source, if known."""
        value = dossier.get("candidate", {}).get("lastResumeUpdatedDate")
        return str(value) if value else None

    @staticmethod
    def build_experience(
        row: dict[str, Any], current_month: dict[str, Any]
    ) -> CareerFactExperience:
        """Turn one work-experience row into a computed experience."""
        start = row["fromDateObject"]
        end = row.get("toDateObject") or current_month
        duration = max(0, month_index(end) - month_index(start))
        source_id = row.get("id")
        return CareerFactExperience(
            source_experience_id=str(source_id) if source_id else None,
            company=row.get("company"),
            role=row.get("position"),
            start_date=month_date(start),
            end_date=month_date(end),
            is_current=row.get("toDateObject") is None,
            duration_months=duration,
            is_shorter_than_12_months=duration < 12,
            transition_reason=(
                row.get("leavingReason") or row.get("transitionReason")
            ),
            responsibilities=row.get("responsibilities") or None,
        )

    @staticmethod
    def build_gaps(
        experiences: list[CareerFactExperience],
    ) -> list[CareerFactGap]:
        """Detect positive gaps between consecutive jobs."""
        gaps: list[CareerFactGap] = []
        for previous, following in zip(
            experiences, experiences[1:], strict=False
        ):
            gap = month_index(
                {
                    "year": int(following.start_date[:4]),
                    "month": int(following.start_date[5:7]),
                }
            ) - month_index(
                {
                    "year": int(previous.end_date[:4]),
                    "month": int(previous.end_date[5:7]),
                }
            )
            if gap > 0:
                gaps.append(
                    CareerFactGap(
                        after_company=previous.company,
                        before_company=following.company,
                        start_date=previous.end_date,
                        end_date=following.start_date,
                        duration_months=gap,
                    )
                )
        return gaps

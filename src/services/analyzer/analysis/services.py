from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from services.analyzer.analysis.open_ai.services import (
    AnalyzerOpenAiService,
)
from services.analyzer.analysis.schemas import EmploymentGap

if TYPE_CHECKING:
    from services.analyzer.analysis.schemas import ResumeAnalysis
    from services.analyzer.schemas import CareerFacts


@final
class ResumeAnalysisService(BaseService):
    """Produce the structured analysis and make chronology authoritative."""

    open_ai_service = AnalyzerOpenAiService()

    @override
    async def execute(
        self,
        dossier: dict[str, Any],
        computed_facts: CareerFacts,
        analysis_id: UUID,
    ) -> ResumeAnalysis:
        """Run the LLM, stamp metadata and overlay computed facts."""
        analysis = await self.open_ai_service.execute(
            dossier=dossier, computed_facts=computed_facts
        )
        self.apply_metadata(analysis=analysis, analysis_id=analysis_id)
        self.apply_career_facts(analysis=analysis, facts=computed_facts)
        return analysis

    def apply_metadata(
        self, analysis: ResumeAnalysis, analysis_id: UUID
    ) -> None:
        """Overwrite model-owned metadata with application-owned values."""
        metadata = analysis.analysis
        metadata.id = str(analysis_id)
        metadata.status = "completed"
        metadata.created_at = datetime.now(UTC).isoformat()
        metadata.model = self.open_ai_service.model

    @staticmethod
    def apply_career_facts(
        analysis: ResumeAnalysis, facts: CareerFacts
    ) -> None:
        """Force deterministic chronology onto the model's output."""
        analysis.candidate.age = facts.age
        analysis.candidate.salary_value = (
            facts.salary.value if facts.salary else None
        )
        analysis.candidate.salary_currency = (
            facts.salary.currency if facts.salary else None
        )
        analysis.candidate.resume_updated_date = facts.resume_updated_date
        source = sorted(facts.experiences, key=lambda item: item.start_date)
        output = sorted(
            analysis.experiences, key=lambda item: item.start_date or ""
        )
        if len(source) != len(output):
            raise ValueError(
                "Модель вернула другое количество мест работы: "
                f"{len(output)} вместо {len(source)}"
            )
        for output_item, source_item in zip(output, source, strict=True):
            output_item.role = source_item.role
            output_item.start_date = source_item.start_date
            output_item.end_date = source_item.end_date
            output_item.duration_months = source_item.duration_months
            output_item.responsibilities = source_item.responsibilities

        summary = analysis.experience_summary
        summary.total_months = facts.total_months
        summary.gaps = [
            EmploymentGap(
                start_date=gap.start_date,
                end_date=gap.end_date,
                duration_months=gap.duration_months,
            )
            for gap in facts.gaps
        ]

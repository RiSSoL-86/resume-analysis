import logging
from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.analyses.choices import AnalysisStatus
from apps.analyses.repository import AnalysisRepository
from apps.common.services.base import BaseService
from services.analyzer.analysis.services import ResumeAnalysisService
from services.analyzer.dashboard.services import DashboardBuilderService
from services.analyzer.facts.services import CareerFactsService

if TYPE_CHECKING:
    from apps.analyses.models import Analysis
    from services.analyzer.analysis.schemas import ResumeAnalysis
    from services.analyzer.dashboard.schemas import Dashboard

logger = logging.getLogger(__name__)


@final
class AnalyzeResumeService(BaseService):
    """Drive one dossier's analysis, delegating each step to a service."""

    analysis_repository = AnalysisRepository()
    career_facts_service = CareerFactsService()
    resume_analysis_service = ResumeAnalysisService()
    dashboard_builder_service = DashboardBuilderService()

    @override
    async def execute(self, analysis_id: UUID) -> Analysis | None:
        """Analyze one dossier, returning it, or None when it is gone."""
        analysis = await self.analysis_repository.get(primary_key=analysis_id)
        if analysis is None:
            logger.warning(msg=f"Analysis {analysis_id} not found; skipping")
            return None

        if analysis.status != AnalysisStatus.PENDING:
            logger.info(
                msg=f"Analysis {analysis_id} is not pending "
                f"({analysis.status=}); skipping"
            )
            return analysis

        if not await self.analysis_repository.claim_for_processing(
            analysis_id=analysis_id
        ):
            logger.info(
                msg=f"Analysis {analysis_id} already claimed; skipping"
            )
            return analysis

        logger.info(msg=f"Analyzing dossier for analysis {analysis_id}")
        try:
            result, dashboard = await self.analyze(analysis)
        except Exception as error:
            logger.exception(msg=f"Analysis {analysis_id} failed")
            await self.analysis_repository.set_status(
                analysis=analysis,
                status=AnalysisStatus.FAILED,
                error_message=str(error),
            )
            return analysis

        await self.analysis_repository.set_status(
            analysis=analysis,
            status=AnalysisStatus.DONE,
            analysis_result=result.model_dump(by_alias=True),
            dashboard=dashboard.model_dump(by_alias=True),
            model_name=result.analysis.model or "",
        )
        logger.info(msg=f"Analysis {analysis_id} completed")
        return analysis

    async def analyze(
        self, analysis: Analysis
    ) -> tuple[ResumeAnalysis, Dashboard]:
        """Run the ordered analysis steps for one dossier.

        Step 1 computes authoritative chronology from the dossier.
        Step 2 runs the LLM analysis and overlays those facts.
        Step 3 projects the result into the dashboard view model.
        """
        dossier = analysis.source_dossier

        computed_facts = await self.career_facts_service.execute(
            dossier=dossier
        )
        result = await self.resume_analysis_service.execute(
            dossier=dossier,
            computed_facts=computed_facts,
            analysis_id=analysis.id,
        )
        dashboard = await self.dashboard_builder_service.execute(
            analysis=result
        )
        return result, dashboard

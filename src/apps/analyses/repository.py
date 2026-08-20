from typing import Any, final
from uuid import UUID

from django.utils import timezone

from apps.analyses.choices import AnalysisStatus
from apps.analyses.models import Analysis
from apps.common.repository import BaseRepository


@final
class AnalysisRepository(BaseRepository[Analysis, UUID]):
    """Persistence operations for resume analyses."""

    model = Analysis

    async def claim_for_processing(self, analysis_id: UUID) -> bool:
        """Atomically move a pending analysis to processing."""
        claimed = await self.model.objects.filter(
            id=analysis_id,
            status=AnalysisStatus.PENDING,
        ).aupdate(
            status=AnalysisStatus.PROCESSING,
            updated_timestamp=timezone.now(),
        )
        return claimed == 1

    @staticmethod
    async def set_status(
        analysis: Analysis,
        status: AnalysisStatus,
        analysis_result: dict[str, Any] | None = None,
        dashboard: dict[str, Any] | None = None,
        model_name: str = "",
        error_message: str = "",
    ) -> Analysis:
        """Persist a status change with any result, dashboard or error."""
        analysis.status = status
        analysis.analysis_result = analysis_result
        analysis.dashboard = dashboard
        analysis.model_name = model_name
        analysis.error_message = error_message
        await analysis.asave(
            update_fields=(
                "status",
                "analysis_result",
                "dashboard",
                "model_name",
                "error_message",
                "updated_timestamp",
            ),
        )
        return analysis

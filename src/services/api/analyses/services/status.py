from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.analyses.repository import AnalysisRepository
from apps.common.services.base import BaseService
from services.api.analyses.exceptions import AnalysisNotFoundError

if TYPE_CHECKING:
    from apps.analyses.models import Analysis


@final
class GetAnalysisStatusService(BaseService):
    """Resolve the current state of an analysis by its identifier."""

    analysis_repository = AnalysisRepository()

    @override
    async def execute(self, analysis_id: UUID) -> Analysis:
        """Return the analysis or raise if it does not exist."""
        analysis = await self.analysis_repository.get(primary_key=analysis_id)
        if analysis is None:
            raise AnalysisNotFoundError
        return analysis

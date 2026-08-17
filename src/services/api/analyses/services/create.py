import json
from typing import final, override

from apps.analyses.choices import AnalysisStatus
from apps.analyses.models import Analysis
from apps.analyses.repository import AnalysisRepository
from apps.common.services.base import BaseService
from services.api.analyses.exceptions import InvalidDossierError
from services.api.analyses.utils import extract_candidate_name
from services.celery_tasks.analyses import analyze_dossier


@final
class CreateAnalysisService(BaseService):
    """Create an analysis record and schedule its processing."""

    analysis_repository = AnalysisRepository()

    @override
    async def execute(self, raw_dossier: bytes) -> Analysis:
        """Parse the dossier, persist a pending analysis and enqueue it."""
        try:
            dossier = json.loads(raw_dossier)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise InvalidDossierError from error

        if not isinstance(dossier, dict):
            raise InvalidDossierError

        analysis = Analysis(
            status=AnalysisStatus.PENDING,
            candidate_name=extract_candidate_name(dossier=dossier),
            source_dossier=dossier,
        )
        analysis = await self.analysis_repository.create(instance=analysis)

        analyze_dossier.delay(analysis_id=str(analysis.id))

        return analysis

from uuid import UUID

from asgiref.sync import async_to_sync
from celery import shared_task

from services.analyzer.services import AnalyzeResumeService


@shared_task(name="analyses.analyze_dossier")
def analyze_dossier(analysis_id: str) -> None:
    """Drive the async analysis orchestrator for the given analysis id."""
    service = AnalyzeResumeService()
    async_to_sync(awaitable=service.execute)(analysis_id=UUID(analysis_id))

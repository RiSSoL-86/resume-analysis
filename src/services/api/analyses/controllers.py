from http import HTTPStatus
from typing import Any, final

from asgiref.sync import sync_to_async
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse
from dmr import Controller, FileMetadata, Path, ResponseSpec, modify, validate
from dmr.errors import ErrorModel
from dmr.parsers import MultiPartParser
from dmr.plugins.pydantic import PydanticSerializer
from dmr.renderers import FileRenderer

from apps.analyses.choices import AnalysisStatus
from services.analyzer.dashboard.schemas import Dashboard
from services.api.analyses.constants import NOTICES, PENDING_STATES
from services.api.analyses.exceptions import (
    AnalysisNotFoundError,
    InvalidDossierError,
)
from services.api.analyses.schemas import (
    AnalysisCreatedResponse,
    AnalysisPath,
    AnalysisStatusResponse,
    DossierUploadPayload,
)
from services.api.analyses.services.create import CreateAnalysisService
from services.api.analyses.services.status import GetAnalysisStatusService
from services.api.analyses.utils import render_html


@final
class AnalysisUploadController(Controller[PydanticSerializer]):
    """Accept a candidate dossier JSON and start its analysis."""

    auth = None
    parsers = (MultiPartParser(),)

    @modify(
        status_code=HTTPStatus.ACCEPTED,
        tags=["Analyses"],
        extra_responses=[
            ResponseSpec(ErrorModel, status_code=HTTPStatus.BAD_REQUEST),
        ],
    )
    async def post(
        self, parsed_file_metadata: FileMetadata[DossierUploadPayload]
    ) -> AnalysisCreatedResponse:
        """Create a pending analysis from the uploaded dossier file."""
        upload = self.request.FILES["file"]
        if not isinstance(upload, UploadedFile):
            raise InvalidDossierError
        raw_dossier = await sync_to_async(upload.read)()

        service = CreateAnalysisService()
        analysis = await service.execute(raw_dossier=raw_dossier)

        return AnalysisCreatedResponse.model_validate(obj=analysis)


@final
class AnalysisStatusController(Controller[PydanticSerializer]):
    """Return the processing state of an analysis."""

    auth = None

    @modify(
        status_code=HTTPStatus.OK,
        tags=["Analyses"],
        extra_responses=[
            ResponseSpec(ErrorModel, status_code=HTTPStatus.NOT_FOUND),
        ],
    )
    async def get(
        self, parsed_path: Path[AnalysisPath]
    ) -> AnalysisStatusResponse:
        """Return the current status of the requested analysis."""
        service = GetAnalysisStatusService()
        analysis = await service.execute(analysis_id=parsed_path.analysis_id)

        return AnalysisStatusResponse(
            id=analysis.id,
            status=analysis.status,
            status_label=str(AnalysisStatus(analysis.status).label),
            candidate_name=analysis.candidate_name,
            error_message=analysis.error_message,
        )


@final
class AnalysisDashboardController(Controller[PydanticSerializer]):
    """Render a finished analysis as an HTML report page."""

    auth = None

    @validate(
        ResponseSpec(
            str,
            status_code=HTTPStatus.OK,
            limit_to_content_types={"text/html"},
            description="Analysis report rendered as HTML",
        ),
        ResponseSpec(
            str,
            status_code=HTTPStatus.NOT_FOUND,
            limit_to_content_types={"text/html"},
            description="Analysis not found",
        ),
        tags=["Analyses"],
        renderers=[FileRenderer("text/html")],
        validate_responses=False,
    )
    async def get(self, parsed_path: Path[AnalysisPath]) -> HttpResponse:
        """Return the report page for the requested analysis as HTML."""
        try:
            analysis = await GetAnalysisStatusService().execute(
                analysis_id=parsed_path.analysis_id,
            )
        except AnalysisNotFoundError:
            return await render_html(
                status=HTTPStatus.NOT_FOUND,
                context={
                    "notice_title": "Анализ не найден",
                    "notice_message": "Проверьте ссылку — такого разбора нет.",
                },
                template_name="analyses/dashboard.html",
                download_name="report",
            )
        status = AnalysisStatus(analysis.status)
        if status == AnalysisStatus.DONE and analysis.dashboard is not None:
            context = self.report_context(analysis.dashboard)
        else:
            context = self.notice_context(status, analysis.error_message)
        return await render_html(
            status=HTTPStatus.OK,
            context=context,
            template_name="analyses/dashboard.html",
            download_name=analysis.candidate_name or "report",
        )

    @staticmethod
    def report_context(dashboard_data: dict[str, Any]) -> dict[str, Any]:
        """Shape the stored dashboard into template-ready values."""
        dashboard = Dashboard.model_validate(dashboard_data)
        return {"d": dashboard, "pending": False}

    @staticmethod
    def notice_context(
        status: AnalysisStatus, error_message: str
    ) -> dict[str, Any]:
        """Build the context for a not-yet-ready analysis."""
        title, message = NOTICES.get(status, ("", ""))
        return {
            "pending": status in PENDING_STATES,
            "notice_title": title,
            "notice_message": error_message or message,
        }

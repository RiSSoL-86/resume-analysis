from http import HTTPStatus
from typing import final

from django.utils.translation import gettext_lazy as _

from services.api.common.exceptions import BaseAPIError


@final
class InvalidDossierError(BaseAPIError):
    """Report an uploaded file that is not a valid JSON dossier."""

    message = _("The uploaded file is not a valid JSON dossier.")
    loc = "file"
    status_code = HTTPStatus.BAD_REQUEST


@final
class AnalysisNotFoundError(BaseAPIError):
    """Report a request for an analysis that does not exist."""

    message = _("Analysis not found.")
    loc = "analysis_id"
    status_code = HTTPStatus.NOT_FOUND

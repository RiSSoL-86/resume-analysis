from typing import final
from uuid import UUID

import pydantic

from services.api.common.schemas import CamelCaseModel


class UploadedDossierFile(pydantic.BaseModel):
    """Validate metadata of the uploaded dossier file."""

    name: str
    size: int = pydantic.Field(gt=0)


@final
class DossierUploadPayload(pydantic.BaseModel):
    """Describe the multipart body of a dossier upload request."""

    file: UploadedDossierFile


@final
class AnalysisPath(pydantic.BaseModel):
    """Describe the path parameters of analysis endpoints."""

    analysis_id: UUID


@final
class AnalysisCreatedResponse(CamelCaseModel):
    """Return the identifier of a freshly created analysis."""

    id: UUID
    status: int


@final
class AnalysisStatusResponse(CamelCaseModel):
    """Return the current processing state of an analysis."""

    id: UUID
    status: int
    status_label: str
    candidate_name: str
    error_message: str

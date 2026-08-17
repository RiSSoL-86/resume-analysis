from dmr.routing import Router, path

from services.api.analyses.controllers import (
    AnalysisDashboardController,
    AnalysisStatusController,
    AnalysisUploadController,
)

router = Router(
    prefix="analyses/",
    urls=[
        path("", AnalysisUploadController.as_view(), name="upload"),
        path(
            "<uuid:analysis_id>/",
            AnalysisStatusController.as_view(),
            name="status",
        ),
        path(
            "<uuid:analysis_id>/dashboard/",
            AnalysisDashboardController.as_view(),
            name="dashboard",
        ),
    ],
)

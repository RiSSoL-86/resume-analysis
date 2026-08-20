from apps.analyses.choices import AnalysisStatus

PENDING_STATES = (AnalysisStatus.PENDING, AnalysisStatus.PROCESSING)
NOTICES: dict[AnalysisStatus, tuple[str, str]] = {
    AnalysisStatus.PENDING: (
        "Анализ в очереди",
        "Отчёт появится автоматически, страница обновляется сама.",
    ),
    AnalysisStatus.PROCESSING: (
        "Анализ выполняется",
        "Отчёт появится автоматически, страница обновляется сама.",
    ),
    AnalysisStatus.FAILED: (
        "Не удалось разобрать резюме",
        "Попробуйте загрузить досье ещё раз.",
    ),
}

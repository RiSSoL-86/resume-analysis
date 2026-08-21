from http import HTTPStatus
from typing import Any
from urllib.parse import quote

from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.template.loader import render_to_string


def extract_candidate_name(dossier: dict[str, Any]) -> str:
    """Build the candidate full name from the master resume, best effort."""
    resumes = dossier.get("resumes")
    if not isinstance(resumes, list) or not resumes:
        return ""

    candidate = dossier.get("candidate") or {}
    master_id = str(candidate.get("masterResumeId") or "")
    resume = next(
        (
            item
            for item in resumes
            if isinstance(item, dict)
            and str(item.get("id") or "") == master_id
        ),
        None,
    )
    if resume is None:
        resume = resumes[0] if isinstance(resumes[0], dict) else {}

    parts = [
        resume.get("lastName"),
        resume.get("firstName"),
        resume.get("middleName"),
    ]
    return " ".join(part for part in parts if part).strip()


async def render_html(
    status: HTTPStatus,
    context: dict[str, Any],
    template_name: str,
    download_name: str = "",
) -> HttpResponse:
    """Render a template to an HTML attachment named <download_name>.html"""

    html = await sync_to_async(
        func=render_to_string,
        thread_sensitive=False,
    )(template_name, context=context)
    response = HttpResponse(
        html,
        status=status,
        content_type="text/html; charset=utf-8",
    )
    if download_name:
        encoded = quote(f"{download_name}.html")
        ascii_name = (
            download_name.encode("ascii", "ignore").decode("ascii").strip()
        )
        fallback = f"{ascii_name}.html" if ascii_name else "report.html"
        response["Content-Disposition"] = (
            f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{encoded}"
        )
    return response

from django.urls import include
from dmr.routing import Router, path

from services.api.analyses import urls as analyses_urls
from services.api.auth import urls as auth_urls
from services.api.users import urls as users_urls

router = Router(
    prefix="",
    urls=[
        path(
            auth_urls.router.prefix,
            include(
                (auth_urls.router.urls, "auth"),
                namespace="auth",
            ),
        ),
        path(
            analyses_urls.router.prefix,
            include(
                (analyses_urls.router.urls, "analyses"),
                namespace="analyses",
            ),
        ),
        path(
            users_urls.router.prefix,
            include(
                (users_urls.router.urls, "users"),
                namespace="users",
            ),
        ),
    ],
)

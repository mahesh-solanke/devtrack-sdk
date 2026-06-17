"""DevTrack SDK - Request tracking middleware for FastAPI and Django."""

from importlib import import_module

from devtrack_sdk.__version__ import __version__

_LAZY_EXPORTS = {
    "DevTrackMiddleware": ("devtrack_sdk.middleware", "DevTrackMiddleware"),
    "devtrack_router": ("devtrack_sdk.controller", "router"),
    "DevTrackDjangoMiddleware": (
        "devtrack_sdk.django_middleware",
        "DevTrackDjangoMiddleware",
    ),
    "track_view": ("devtrack_sdk.django_views", "track_view"),
    "stats_view": ("devtrack_sdk.django_views", "stats_view"),
    "DevTrackView": ("devtrack_sdk.django_views", "DevTrackView"),
    "devtrack_urlpatterns": ("devtrack_sdk.django_urls", "devtrack_urlpatterns"),
    "devtrack_cbv_urlpatterns": (
        "devtrack_sdk.django_urls",
        "devtrack_cbv_urlpatterns",
    ),
}


def __getattr__(name):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attribute_name = _LAZY_EXPORTS[name]
    module = import_module(module_name)
    attribute = getattr(module, attribute_name)
    globals()[name] = attribute
    return attribute


__all__ = [
    "__version__",
    # FastAPI
    "DevTrackMiddleware",
    "devtrack_router",
    # Django
    "DevTrackDjangoMiddleware",
    "track_view",
    "stats_view",
    "DevTrackView",
    "devtrack_urlpatterns",
    "devtrack_cbv_urlpatterns",
]

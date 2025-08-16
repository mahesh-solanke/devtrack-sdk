"""
Test URL configuration for DevTrack SDK Django tests
"""

from devtrack_sdk.django_urls import devtrack_urlpatterns

urlpatterns = [
    # Include DevTrack URLs for testing
    *devtrack_urlpatterns,
]

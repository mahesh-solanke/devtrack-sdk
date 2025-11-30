#!/usr/bin/env python3
"""
Manual verification script for DevTrack SDK v0.4.0
Tests both FastAPI and Django integrations
"""
import os
import sys
import uuid
from pathlib import Path

from devtrack_sdk.controller.devtrack_routes import router as devtrack_router
from devtrack_sdk.database import DevTrackDB, init_db
from devtrack_sdk.middleware.base import DevTrackMiddleware

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


# Test FastAPI
print("=" * 60)
print("Testing FastAPI Integration")
print("=" * 60)

try:
    from fastapi import FastAPI
    from starlette.testclient import TestClient

    # Create test database
    db_path = f"/tmp/manual_test_{uuid.uuid4().hex}.db"
    init_db(db_path)

    app = FastAPI()
    app.include_router(devtrack_router)
    db = DevTrackDB(db_path)
    app.add_middleware(DevTrackMiddleware, db_instance=db)

    @app.get("/")
    async def root():
        return {"message": "Hello"}

    @app.get("/error")
    def error_route():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not Found")

    @app.post("/users")
    async def create_user():
        return {"id": 1, "name": "Test User"}

    client = TestClient(app)

    # Test 1: Basic logging
    print("\n1. Testing basic request logging...")
    response = client.get("/")
    assert response.status_code == 200
    print("   ✅ GET / - Logged successfully")

    # Test 2: Error logging
    print("\n2. Testing error logging...")
    response = client.get("/error")
    assert response.status_code == 404
    print("   ✅ GET /error - Error logged successfully")

    # Test 3: POST request
    print("\n3. Testing POST request logging...")
    response = client.post("/users", json={"name": "Test"})
    assert response.status_code == 200
    print("   ✅ POST /users - Logged successfully")

    # Test 4: Stats endpoint
    print("\n4. Testing stats endpoint...")
    response = client.get("/__devtrack__/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "entries" in data
    print(f"   ✅ Stats endpoint - {data['total']} entries found")

    # Test 5: Traffic metrics (v0.4.0)
    print("\n5. Testing traffic metrics endpoint (v0.4.0)...")
    response = client.get("/__devtrack__/metrics/traffic")
    assert response.status_code == 200
    data = response.json()
    assert "traffic" in data
    print("   ✅ Traffic metrics endpoint - Working")

    # Test 6: Error metrics (v0.4.0)
    print("\n6. Testing error metrics endpoint (v0.4.0)...")
    response = client.get("/__devtrack__/metrics/errors")
    assert response.status_code == 200
    data = response.json()
    assert "error_trends" in data
    assert "top_failing_routes" in data
    print("   ✅ Error metrics endpoint - Working")

    # Test 7: Performance metrics (v0.4.0)
    print("\n7. Testing performance metrics endpoint (v0.4.0)...")
    response = client.get("/__devtrack__/metrics/perf")
    assert response.status_code == 200
    data = response.json()
    assert "latency_over_time" in data
    assert "overall_stats" in data
    print("   ✅ Performance metrics endpoint - Working")

    # Test 8: Consumer segmentation (v0.4.0)
    print("\n8. Testing consumer segmentation endpoint (v0.4.0)...")
    response = client.get("/__devtrack__/consumers")
    assert response.status_code == 200
    data = response.json()
    assert "segments" in data
    print("   ✅ Consumer segmentation endpoint - Working")

    # Test 9: Dashboard endpoint (v0.4.0)
    print("\n9. Testing dashboard endpoint (v0.4.0)...")
    response = client.get("/__devtrack__/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    print("   ✅ Dashboard endpoint - Working")

    # Test 10: Delete logs
    print("\n10. Testing delete logs...")
    response = client.delete("/__devtrack__/logs?all_logs=true")
    assert response.status_code == 200
    data = response.json()
    assert data["deleted_count"] > 0
    print(f"   ✅ Delete logs - {data['deleted_count']} logs deleted")

    # Cleanup
    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)

    print("\n✅ FastAPI Integration: ALL TESTS PASSED")

except Exception as e:
    print(f"\n❌ FastAPI Integration: FAILED - {e}")
    import traceback

    traceback.print_exc()

# Test Django
print("\n" + "=" * 60)
print("Testing Django Integration")
print("=" * 60)

try:
    import django
    from django.conf import settings
    from django.test import RequestFactory

    # Configure Django
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY="test-secret-key",
            ROOT_URLCONF="tests.test_urls",
            MIDDLEWARE=[
                "devtrack_sdk.django_middleware.DevTrackDjangoMiddleware",
            ],
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
            ],
        )
        django.setup()

    from devtrack_sdk.django_middleware import DevTrackDjangoMiddleware
    from devtrack_sdk.django_views import stats_view

    factory = RequestFactory()

    def mock_get_response(request):
        return type("Response", (), {"status_code": 200, "content": b"test"})()

    middleware = DevTrackDjangoMiddleware(mock_get_response)

    # Test 1: Middleware initialization
    print("\n1. Testing middleware initialization...")
    assert middleware is not None
    assert "/__devtrack__/stats" in middleware.skip_paths
    print("   ✅ Middleware initialized correctly")

    # Test 2: Stats view
    print("\n2. Testing stats view...")
    request = factory.get("/__devtrack__/stats")
    response = stats_view(request)
    assert response.status_code == 200
    print("   ✅ Stats view - Working")

    # Test 3: Custom exclude paths
    print("\n3. Testing custom exclude paths...")
    custom_middleware = DevTrackDjangoMiddleware(
        mock_get_response, exclude_path=["/custom/"]
    )
    assert "/custom/" in custom_middleware.skip_paths
    print("   ✅ Custom exclude paths - Working")

    print("\n✅ Django Integration: ALL TESTS PASSED")

except Exception as e:
    print(f"\n❌ Django Integration: FAILED - {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("Manual Verification Complete")
print("=" * 60)

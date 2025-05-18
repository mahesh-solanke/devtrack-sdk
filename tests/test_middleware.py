import pytest
from fastapi import FastAPI, HTTPException
from starlette.testclient import TestClient

from devtrack_sdk.controller.devtrack_routes import router as devtrack_router
from devtrack_sdk.middleware.base import DevTrackMiddleware


@pytest.fixture
def app_with_middleware():
    app = FastAPI()
    app.include_router(devtrack_router)
    app.add_middleware(DevTrackMiddleware, api_key="test-key")

    @app.get("/")
    async def root():
        return {"message": "Hello"}

    @app.get("/error")
    def error_route():
        raise HTTPException(status_code=400, detail="Bad Request")

    return app


def test_root_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    response = client.get("/")
    assert response.status_code == 200
    assert len(DevTrackMiddleware.stats) == 1
    assert DevTrackMiddleware.stats[0]["path"] == "/"
    assert DevTrackMiddleware.stats[0]["method"] == "GET"


def test_error_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    client.get("/error")
    assert len(DevTrackMiddleware.stats) == 1
    assert DevTrackMiddleware.stats[0]["status_code"] == 400


def test_internal_stats_endpoint(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    client.get("/")
    response = client.get("/__devtrack__/stats")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert "entries" in body
    assert isinstance(body["entries"], list)

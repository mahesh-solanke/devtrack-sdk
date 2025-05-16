from fastapi import FastAPI

from devtrack_sdk.controller.devtrack_routes import router as devtrack_router
from devtrack_sdk.middleware.base import DevTrackMiddleware

app = FastAPI()

app.include_router(devtrack_router)
app.add_middleware(DevTrackMiddleware, api_key="dummy")


@app.get("/")
async def root():
    return {"message": "Hello from DevTrack!"}


@app.get("/slow")
async def slow():
    import time

    time.sleep(1)
    return {"message": "This was a slow request!"}

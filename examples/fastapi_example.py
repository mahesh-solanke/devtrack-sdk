import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from devtrack_sdk.controller.devtrack_routes import router as devtrack_router
from devtrack_sdk.middleware.base import DevTrackMiddleware

app = FastAPI()

app.include_router(devtrack_router)
middleware_config = {
    "development": {
        "skip_paths": ["/get_token", "/user/password", "/admin"],
    },
    "production": {
        "skip_paths": ["/admin", "/user/password"],
    },
}
env = os.getenv("ENV", "development")
app.add_middleware(
    DevTrackMiddleware, exclude_path=middleware_config[env]["skip_paths"]
)


class Data(BaseModel):
    username: str
    password: str


@app.get("/")
async def root():
    return {"message": "Hello from DevTrack!"}


@app.post("/slow/{seconds}")
async def slow(seconds: int | float, value: str, data: Data):
    import time

    time.sleep(seconds)
    return {"message": "This was a slow request!"}


@app.get("/error")
async def error():
    raise HTTPException(status_code=400, detail="This is an error")

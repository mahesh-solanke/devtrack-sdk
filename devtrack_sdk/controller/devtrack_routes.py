from fastapi import APIRouter, Request

from devtrack_sdk.middleware.base import DevTrackMiddleware

router = APIRouter()


@router.post("/__devtrack__/track", include_in_schema=False)
async def track(req: Request):
    try:
        data = await req.json()
    except Exception:
        data = {"error": "Invalid JSON"}
    DevTrackMiddleware.stats.append(data)
    return {"ok": True}


@router.get("/__devtrack__/stats", include_in_schema=False)
async def stats():
    return {"total": len(DevTrackMiddleware.stats), "entries": DevTrackMiddleware.stats}

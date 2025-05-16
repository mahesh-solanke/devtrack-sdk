
from fastapi import FastAPI, Request
from devtrack_sdk.middleware import DevTrackMiddleware

app = FastAPI()

@app.post("/track")
async def track(req: Request):
    """Receives tracking data from DevTrackMiddleware.
    
    This endpoint is used internally by the middleware to log request metadata 
    (path, method, status code, client IP). It is not intended for direct use.
    
    Request Body (JSON):
    {
        "path": str,        # Request path (e.g. "/slow") 
        "method": str,      # HTTP method (e.g. "GET")
        "status_code": int, # Response status code (e.g. 200)
        "client": str       # Client IP address
    }
    
    Returns:
        200 OK on success
        400 Bad Request if JSON is invalid
        405 Method Not Allowed if not POST
    
    Note:
        This endpoint is excluded from middleware tracking to avoid recursion.
    """
    try:
        data = await req.json()
        return {"status": "success", "message": "Track data received"}
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

@app.get("/stats")
def stats():
    return {
        "total": len(DevTrackMiddleware.stats),
        "entries": DevTrackMiddleware.stats
    }

app.add_middleware(
    DevTrackMiddleware,
    api_key="dummy",
    backend_url="http://localhost:8000/track"
)

@app.get("/")
async def root():
    return {"message": "Hello from DevTrack!"}

@app.get("/slow")
async def slow():
    import time
    time.sleep(1)
    return {"message": "This was a slow request!"}

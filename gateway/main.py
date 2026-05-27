import httpx
from fastapi import FastAPI, Request, Response

from config import settings

app = FastAPI(title="gateway", version="1.0.0")

ROUTES: dict[str, str] = {
    "users":      settings.user_service_url,
    "games":      settings.game_service_url,
    "activities": settings.activity_service_url,
    # "notifications": settings.notification_service_url,  # Added in Module 4
    # "auth":          settings.auth_service_url,           # Added in Module 6
    # "consent":       settings.logging_service_url,        # Added in Module 5
    # "logs":          settings.logging_service_url,        # Added in Module 5
}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(request: Request, path: str):
    # Step 1 — parse the path to extract the resource name
    segments = path.split("/")
    if len(segments) < 2:
        return Response(status_code=404, content="Not found")

    # Step 2 — look up the resource in the routing table
    resource = segments[1]
    target_base = ROUTES.get(resource)
    if target_base is None:
        return Response(status_code=404, content=f"Unknown resource: {resource}")

    # Step 3 — build the target URL and forward the request
    target_url = f"{target_base}/{path}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers.raw,
                content=await request.body(),
                params=request.query_params,
            )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type"),
        )

    # Step 4 — handle unreachable downstream service
    except httpx.RequestError:
        return Response(status_code=503, content="Service unavailable")
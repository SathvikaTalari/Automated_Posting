
from fastapi import FastAPI

from app.schemas import PostingRequest
from app.services.posting_service import posting_service

app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description="Publish messages across multiple platforms through one API.",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "Automated Posting API is running"
    }


@app.post("/posting")
async def create_post(request: PostingRequest):

    results = await posting_service.publish_to_all(
        request.message
    )

    successful = sum(
        result.status == "success"
        for result in results
    )

    failed = sum(
        result.status == "failed"
        for result in results
    )

    return {
        "success": failed == 0,
        "status": (
            "completed" if failed == 0
            else "partial" if successful > 0
            else "failed"
        ),
        "message": request.message,
        "total_platforms": len(results),
        "successful": successful,
        "failed": failed,
        "results": results
    }

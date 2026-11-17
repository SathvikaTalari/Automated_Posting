from fastapi import FastAPI

from app.schemas import PostingRequest

app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description="Publish messages across multiple platforms through one API.",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Automated Posting API is running"}


@app.post("/posting")
async def create_post(request: PostingRequest):
    return {
        "success": True,
        "message": request.message
    }

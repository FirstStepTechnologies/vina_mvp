from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class VideoResponse(BaseModel):
    video_url: str
    title: str
    description: str

@router.get("/dummy-video", response_model=VideoResponse)
async def get_dummy_video():
    """
    Returns a fixed Cloudinary video URL for frontend testing.
    """
    return VideoResponse(
        # Standard Cloudinary demo video
        video_url="https://res.cloudinary.com/demo/video/upload/dog.mp4",
        title="Sample Video for Testing",
        description="This is a dummy video returned for frontend integration testing."
    )

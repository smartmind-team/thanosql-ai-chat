from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException

class FeedbackRequest(BaseModel):
    id: str = Field(..., description="Unique identifier for the feedback")
    question: str = Field(..., description="The question text")
    answer: str = Field(..., description="The answer text")
    tags: Optional[List[str]] = Field(None, description="Optional list of related tags")
    feedback_status: str = Field(..., description="Feedback status, must be 'like' or 'dislike'")

    @classmethod
    def validate_feedback_status(cls, value: str) -> str:
        if value not in ["like", "dislike"]:
            raise ValueError("feedback_status must be either 'like' or 'dislike'")
        return value


def process_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    try:
        FeedbackRequest.validate_feedback_status(request.feedback_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


    return {
        "feedback_status": request.feedback_status,
    }

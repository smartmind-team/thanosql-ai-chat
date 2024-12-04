from typing import Dict
from pydantic import BaseModel, Field
from fastapi import HTTPException

class FeedbackRequest(BaseModel):
    # Feedback request model with required fields
    id: str = Field(..., description="Unique identifier for the feedback")
    feedback_status: str = Field(..., description="Must be 'like' or 'dislike'")

    @classmethod
    def validate_feedback_status(cls, value: str) -> str:
        """
        Validate 'feedback_status' to ensure it's either 'like' or 'dislike'.
        """
        if value not in ["like", "dislike"]:
            raise ValueError("feedback_status must be either 'like' or 'dislike'")
        return value


def process_feedback(request: FeedbackRequest) -> Dict[str, str]: 
    """
    Validate feedback and return the status.
    """
    try:
        FeedbackRequest.validate_feedback_status(request.feedback_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"feedback_status": request.feedback_status}

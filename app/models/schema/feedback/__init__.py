from pydantic import BaseModel, Field

class FeedbackRequest(BaseModel):
    # Feedback request model with updated fields
    message_id: str = Field(..., description="Unique identifier for the feedback message")
    session_id: str = Field(..., description="Unique identifier for the user session")
    feedback_type: str = Field(..., description="Context type for the feedback")
    feedback_status: str = Field(..., description="Must be 'like' or 'dislike'")

    @classmethod
    def validate_feedback_status(cls, value: str) -> str:
        """
        Validate 'feedback_status' to ensure it's either 'like' or 'dislike'.
        """
        if value not in ["like", "dislike"]:
            raise ValueError("feedback_status must be either 'like' or 'dislike'")
        return value

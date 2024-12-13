from typing import Dict
from pydantic import BaseModel, Field
from fastapi import HTTPException
import psycopg2
import logging

logger = logging.getLogger(__name__)

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


def process_feedback(request: FeedbackRequest) -> Dict[str, str]: 
    """
    Validate feedback and return the status.
    """
    try:
        FeedbackRequest.validate_feedback_status(request.feedback_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    connection = psycopg2.connect(host='18.119.33.153', dbname='default_database', user='thanosql_user', password='thanosql', port=8821)
    cursor = connection.cursor()
    logger.info(f"feedback request: {request}")
    cursor.execute(f"""INSERT INTO feedback (session_id, message_id, type, status) 
                       VALUES ('{request.session_id}', '{request.message_id}', '{request.feedback_type}', '{request.feedback_status}');
                    """)
    connection.commit()
    cursor.close()
    connection.close()
    return { "feedback_status": request.feedback_status }

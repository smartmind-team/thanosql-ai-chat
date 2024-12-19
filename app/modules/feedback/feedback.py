from typing import Dict

from fastapi import HTTPException
from models.schema import feedback
from modules.database import pg
from utils import logger


def process_feedback(request: feedback.FeedbackRequest) -> Dict[str, str]:
    """
    Validate feedback and return the status.
    """
    try:
        feedback.FeedbackRequest.validate_feedback_status(request.feedback_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(f"feedback request: {request}")
    query = "INSERT INTO feedback (session_id, message_id, type, status)"
    query += " VALUES (%s, %s, %s, %s)"

    pg.execute(
        query,
        (
            request.session_id,
            request.message_id,
            request.feedback_type,
            request.feedback_status,
        ),
    )

    return {"feedback_status": request.feedback_status}

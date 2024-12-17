import sys
from pathlib import Path

from typing import Dict
from fastapi import HTTPException

sys.path.append(Path(__file__).parents[1])
from utils.logger import logger
from models.schema import feedback
from modules.database import pg


def process_feedback(request: feedback.FeedbackRequest) -> Dict[str, str]:
    """
    Validate feedback and return the status.
    """
    try:
        feedback.FeedbackRequest.validate_feedback_status(request.feedback_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(f"feedback request: {request}")
    query = f"""INSERT INTO feedback (session_id, message_id, type, status) 
                VALUES ('{request.session_id}', '{request.message_id}', '{request.feedback_type}', '{request.feedback_status}');
            """
    pg.execute(query)

    return {"feedback_status": request.feedback_status}

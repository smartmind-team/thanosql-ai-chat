from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    id: Optional[str] = ""
    question: Optional[str] = ""  
    answer: Optional[str] = ""  
    tags: Optional[List[str]] = None  
    feedback_status: Optional[str] = "none" 


def process_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.feedback_status not in ["like", "dislike", "none"]:
        raise HTTPException(status_code=400, detail="Invalid feedback status")

    print(request.feedback_status)

    return {
        "feedback_status": request.feedback_status,
    }
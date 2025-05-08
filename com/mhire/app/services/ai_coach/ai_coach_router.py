import logging

from fastapi import APIRouter, HTTPException

from com.mhire.app.services.ai_coach.ai_coach import AICoach
from .ai_coach_schema import ChatRequest, ChatResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/coach",
    tags=["AI Coach"],
    responses={404: {"description": "Not found"}}
)

# Initialize AI Coach
ai_coach = AICoach()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_coach(request: ChatRequest):
    """
    Chat with the friendly AI fitness coach for personalized guidance and motivation
    """
    try:
        response = await ai_coach.chat(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
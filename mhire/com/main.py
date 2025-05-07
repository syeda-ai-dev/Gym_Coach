from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mhire.com.app.services.ai_coach.ai_coach_router import router as ai_coach_router
from mhire.com.app.responses.network_responses import NetworkResponse

app = FastAPI(
    title="Gym Coach API",
    description="AI-powered Gym and Health coaching application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

network_response = NetworkResponse()

# Register routers
app.include_router(ai_coach_router)

@app.get("/")
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return network_response.success_response(
        http_code=NetworkResponse.HttpStatus.SUCCESS,
        message="Server is healthy",
        data={"status": "running"}
    )
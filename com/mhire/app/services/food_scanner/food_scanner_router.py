import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, PlainTextResponse

from com.mhire.app.services.food_scanner.food_scanner import FoodScanner
from com.mhire.app.services.food_scanner.food_scanner_schema import FoodScanResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/food-scanner",
    tags=["Food Scanner"],
    responses={404: {"description": "Not found"}}
)

# Initialize Food Scanner
food_scanner = FoodScanner()

@router.post("/analyze")
async def analyze_food(image: UploadFile = File(...)):
    """
    Analyze a food image and return nutritional information
    """
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        analysis = await food_scanner.analyze_food_image(image)
        
        # Extract the raw analysis text from the health_benefits field where we stored it
        raw_analysis = analysis.health_benefits[0] if analysis.health_benefits else "No analysis available"
        
        # Return the raw text directly
        return JSONResponse(content={"success": True, "analysis": raw_analysis})
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
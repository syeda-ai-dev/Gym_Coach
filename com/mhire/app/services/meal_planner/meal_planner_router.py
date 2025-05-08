import logging
from fastapi import APIRouter, HTTPException
from com.mhire.app.services.meal_planner.meal_planner import MealPlanner
from com.mhire.app.services.meal_planner.meal_planner_schema import UserProfile, DailyMealPlan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/meal-planner",
    tags=["Meal Planner"],
    responses={404: {"description": "Not found"}}
)

meal_planner = MealPlanner()

@router.post("/generate", response_model=DailyMealPlan)
async def generate_meal_plan(profile: UserProfile):
    """
    Generate a customized daily meal plan based on user profile
    """
    try:
        meal_plan = await meal_planner.generate_meal_plan(profile)
        return meal_plan
    except Exception as e:
        logger.error(f"Error in generate meal plan endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
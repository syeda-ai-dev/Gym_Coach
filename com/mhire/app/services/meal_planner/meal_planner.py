import logging
import re
import json
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from com.mhire.app.config.config import Config
from .meal_planner_schema import UserProfile, DailyMealPlan, Meal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MealPlanner:
    def __init__(self):
        try:
            config = Config()
            self.llm = ChatOpenAI(
                openai_api_key=config.openai_api_key,
                model=config.model_name,
                temperature=1  # Lower temperature for more consistent formatting
            )
        except Exception as e:
            logger.error(f"Error initializing MealPlanner: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize Meal Planner: {str(e)}")

    def _create_meal_from_json(self, meal_json):
        """Create a Meal object from JSON data"""
        return Meal(
            name=meal_json["name"],
            description=meal_json["description"],
            calories=float(meal_json["calories"]),
            protein=float(meal_json["protein"]),
            carbs=float(meal_json["carbs"]),
            fat=float(meal_json["fat"]),
            rationale=meal_json["rationale"],
            preparation_steps=meal_json["preparation_steps"]
        )
    
    async def generate_meal_plan(self, profile: UserProfile) -> DailyMealPlan:
        try:
            user_prompt = f"""Create a personalized daily meal plan based on these user details:
            Goal: {profile.primary_goal}
            Weight: {profile.weight_kg}kg
            Height: {profile.height_cm}cm
            Meat Eater: {profile.is_meat_eater}
            Lactose Intolerant: {profile.is_lactose_intolerant}
            Allergies: {', '.join(profile.allergies)}
            Eating Style: {profile.eating_style}
            Caffeine: {profile.caffeine_consumption}
            Sugar: {profile.sugar_consumption}

            You MUST respond with a valid JSON object containing personalized meal recommendations appropriate for this specific user. Return ONLY a JSON object matching this structure:
        
            {{
              "breakfast": {{
                "name": "[GENERATE APPROPRIATE NAME]",
                "description": "[GENERATE BRIEF DESCRIPTION]",
                "calories": [APPROPRIATE CALORIE NUMBER],
                "protein": [APPROPRIATE PROTEIN GRAMS],
                "carbs": [APPROPRIATE CARB GRAMS],
                "fat": [APPROPRIATE FAT GRAMS],
                "rationale": "[EXPLAIN WHY THIS MEAL FITS USER'S NEEDS]",
                "preparation_steps": ["[STEP 1]", "[STEP 2]", "..."]
              }},
              "lunch": {{
                "name": "[GENERATE APPROPRIATE NAME]",
                "description": "[GENERATE BRIEF DESCRIPTION]",
                "calories": [APPROPRIATE CALORIE NUMBER],
                "protein": [APPROPRIATE PROTEIN GRAMS],
                "carbs": [APPROPRIATE CARB GRAMS],
                "fat": [APPROPRIATE FAT GRAMS],
                "rationale": "[EXPLAIN WHY THIS MEAL FITS USER'S NEEDS]",
                "preparation_steps": ["[STEP 1]", "[STEP 2]", "..."]
              }},
              "snack": {{
                "name": "[GENERATE APPROPRIATE NAME]",
                "description": "[GENERATE BRIEF DESCRIPTION]",
                "calories": [APPROPRIATE CALORIE NUMBER],
                "protein": [APPROPRIATE PROTEIN GRAMS],
                "carbs": [APPROPRIATE CARB GRAMS],
                "fat": [APPROPRIATE FAT GRAMS],
                "rationale": "[EXPLAIN WHY THIS MEAL FITS USER'S NEEDS]",
                "preparation_steps": ["[STEP 1]", "[STEP 2]", "..."]
              }},
              "dinner": {{
                "name": "[GENERATE APPROPRIATE NAME]",
                "description": "[GENERATE BRIEF DESCRIPTION]",
                "calories": [APPROPRIATE CALORIE NUMBER],
                "protein": [APPROPRIATE PROTEIN GRAMS],
                "carbs": [APPROPRIATE CARB GRAMS],
                "fat": [APPROPRIATE FAT GRAMS],
                "rationale": "[EXPLAIN WHY THIS MEAL FITS USER'S NEEDS]",
                "preparation_steps": ["[STEP 1]", "[STEP 2]", "..."]
              }}
            }}
        
            IMPORTANT: 
            - Create realistic, nutritionally appropriate meals for this user's specific profile and goal
            - All nutritional values must be numbers without units (no "g" suffix)
            - Ensure preparation_steps is an array of strings with clear cooking/preparation instructions
            - Provide accurate nutritional values based on the ingredients
            - The response must be a valid JSON object with NO text outside the JSON
            - For a user trying to {profile.primary_goal}, adjust calories and macros accordingly
            """

            response = self.llm.invoke(user_prompt)
            content = response.content.strip()
        
            # Log response for debugging
            logger.info(f"LLM response starts with: {content[:100]}...")
        
            try:
                meal_plan_data = json.loads(content)
            
                # Validate required keys
                required_keys = ["breakfast", "lunch", "snack", "dinner"]
                for key in required_keys:
                    if key not in meal_plan_data:
                        raise ValueError(f"Missing required key: {key}")
                
                    # Validate meal object structure
                    meal_keys = ["name", "description", "calories", "protein", "carbs", "fat", "rationale", "preparation_steps"]
                    for meal_key in meal_keys:
                        if meal_key not in meal_plan_data[key]:
                            raise ValueError(f"Missing required key in {key}: {meal_key}")
            
                return DailyMealPlan(
                    breakfast=self._create_meal_from_json(meal_plan_data["breakfast"]),
                    lunch=self._create_meal_from_json(meal_plan_data["lunch"]),
                    snack=self._create_meal_from_json(meal_plan_data["snack"]),
                    dinner=self._create_meal_from_json(meal_plan_data["dinner"])
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from LLM response: {e}")
                raise ValueError(f"Invalid JSON format from LLM: {e}")

        except Exception as e:
            logger.error(f"Error generating meal plan: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate meal plan: {str(e)}")
import logging
from fastapi import HTTPException, UploadFile
import base64
from typing import List
from openai import OpenAI
from com.mhire.app.config.config import Config
from .food_scanner_schema import FoodAnalysis, NutritionInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FoodScanner:
    def __init__(self):
        try:
            config = Config()
            self.client = OpenAI(api_key=config.openai_api_key)
            self.model = config.model_name
        except Exception as e:
            logger.error(f"Error initializing FoodScanner: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize Food Scanner: {str(e)}")

    async def analyze_food_image(self, image: UploadFile) -> FoodAnalysis:
        try:
            # Read and encode image
            image_content = await image.read()
            base64_image = base64.b64encode(image_content).decode('utf-8')

            # Prepare the message for GPT-4 Vision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a nutritional analysis expert. Analyze the food image and provide:
                        1. List of identified food items
                        2. Estimated nutritional information
                        3. Health benefits
                        4. Potential concerns
                        5. Serving suggestions or alternatives"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "image_url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            # Process the response
            analysis = self._parse_response(response.choices[0].message.content)
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing food image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to analyze food image: {str(e)}")

    def _parse_response(self, response_text: str) -> FoodAnalysis:
        try:
            # For demonstration, using placeholder values
            # In production, implement proper parsing of the AI response
            return FoodAnalysis(
                food_items=["Example Food 1", "Example Food 2"],
                nutrition=NutritionInfo(
                    calories=500.0,
                    protein=20.0,
                    carbs=60.0,
                    fat=15.0
                ),
                health_benefits=["Rich in vitamins", "High in fiber"],
                concerns=["Moderate sodium content"],
                serving_suggestions=["Consider whole grain alternatives"]
            )
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to parse analysis: {str(e)}")
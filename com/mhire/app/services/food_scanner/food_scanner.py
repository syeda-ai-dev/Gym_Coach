import logging
import base64
from fastapi import HTTPException, UploadFile
from openai import OpenAI
from com.mhire.app.config.config import Config
from .food_scanner_schema import FoodScanResponse, FoodAnalysis, NutritionInfo

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
            # Check if file is an image
            if not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
                
            # Read and encode image
            image_content = await image.read()
            base64_image = base64.b64encode(image_content).decode('utf-8')
            
            # Determine the content type for the data URL
            content_type = image.content_type  # e.g., "image/jpeg", "image/png"
            data_url = f"data:{content_type};base64,{base64_image}"

            # Prepare the system and user messages
            system_message = """You are a precise nutritional analysis expert with expertise in visual food recognition.
            When you see a food image, provide this information in a clear format:
            
            1. List of all food items visible in the image
            2. Nutritional information (calories, protein, carbs, fat)
            3. Health benefits
            4. Potential dietary concerns
            5. Serving suggestions or alternatives
            
            Be specific and detailed in your analysis."""
            
            user_message = "Analyze this food image and provide nutritional information and dietary insights."

            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_message},
                        {"type": "image_url", "image_url": data_url}
                    ]}
                ],
                max_tokens=800,
                temperature=0.3
            )

            # Get the raw response text
            analysis_text = response.choices[0].message.content.strip()
            
            # Create a simplified FoodAnalysis object with text analysis
            # For food_items, create a placeholder list with one item containing the analysis
            return FoodAnalysis(
                food_items=["See detailed analysis below"],
                nutrition=NutritionInfo(
                    calories=0.0,  # Placeholder values since we're using raw text
                    protein=0.0,
                    carbs=0.0,
                    fat=0.0
                ),
                health_benefits=[analysis_text],  # Put the full analysis text here
                concerns=[],
                serving_suggestions=[]
            )

        except Exception as e:
            logger.error(f"Error analyzing food image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to analyze food image: {str(e)}")
import logging
import base64
from fastapi import HTTPException, UploadFile
from openai import OpenAI
from com.mhire.app.config.config import Config
from com.mhire.app.services.food_scanner.food_scanner_schema import FoodScanResponse, FoodAnalysis, NutritionInfo

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
            # Read image content
            image_content = await image.read()
            base64_image = base64.b64encode(image_content).decode('utf-8')

            # Create API request with correct image format
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a precise nutritional analysis expert with expertise in visual food recognition.
                        Analyze the food image and provide detailed information in this specific format:

                        1. Food Items: List all visible food items with portion estimates
                         2. Nutritional Information:
                           - Total Calories (kcal)
                           - Protein (g)
                           - Carbohydrates (g)
                           - Fat (g)
                           - Portion Size
                        3. Health Benefits: List specific health benefits of the ingredients
                        4. Potential Concerns: Note any dietary concerns or warnings
                        5. Serving Suggestions: Provide alternative preparations or complementary foods

                        Be specific and quantitative in your analysis. If exact values aren't possible, 
                        provide reasonable estimates based on standard serving sizes."""
                    },
                   {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this food image and provide detailed nutritional information."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image.content_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_completion_tokens=1000,
                temperature=1.0
            )

            # Rest of your existing code...
    
            # Extract the analysis text
            analysis_text = response.choices[0].message.content.strip()
            
            # Parse the response to extract structured information
            parsed_info = self._parse_analysis(analysis_text)
            
            return FoodAnalysis(
                food_items=parsed_info["food_items"],
                nutrition=NutritionInfo(
                    calories=parsed_info["calories"],
                    protein=parsed_info["protein"],
                    carbs=parsed_info["carbs"],
                    fat=parsed_info["fat"],
                    portion_size=parsed_info["portion_size"]
                ),
                health_benefits=parsed_info["health_benefits"],
                concerns=parsed_info["concerns"],
                serving_suggestions=parsed_info["serving_suggestions"],
                detailed_analysis=analysis_text
            )

        except Exception as e:
            logger.error(f"Error analyzing food image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to analyze food image: {str(e)}")

    def _parse_analysis(self, text: str) -> dict:
        """Parse the AI response into structured data"""
        lines = text.split('\n')
        result = {
            "food_items": [],
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
            "portion_size": "Standard serving",
            "health_benefits": [],
            "concerns": [],
            "serving_suggestions": []
        }
    
        current_section = None
        buffer = []
    
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            lower_line = line.lower()
        
            # Section headers
            if "1. food items" in lower_line:
                current_section = "food_items"
                continue
            elif "2. nutritional information" in lower_line:
                current_section = "nutrition"
                continue
            elif "3. health benefits" in lower_line:
                current_section = "health_benefits"
                continue
            elif "4. potential concerns" in lower_line:
                current_section = "concerns"
                continue
            elif "5. serving suggestions" in lower_line:
                current_section = "serving_suggestions"
                continue
            
            # Parse content based on section
            if current_section == "food_items":
                if line.startswith('-') or line.startswith('•'):
                    result["food_items"].append(line.lstrip('- •').strip())
                
            elif current_section == "nutrition":
                if "calories" in lower_line:
                    try:
                        value = ''.join(filter(str.isdigit, line))
                        if value:
                            result["calories"] = float(value)
                    except ValueError:
                        pass
                elif "protein" in lower_line:
                    try:
                        value = ''.join(filter(str.isdigit, line))
                        if value:
                            result["protein"] = float(value)
                    except ValueError:
                        pass
                elif "carbohydrate" in lower_line or "carbs" in lower_line:
                    try:
                        value = ''.join(filter(str.isdigit, line))
                        if value:
                            result["carbs"] = float(value)
                    except ValueError:
                        pass
                elif "fat" in lower_line:
                    try:
                        value = ''.join(filter(str.isdigit, line))
                        if value:
                            result["fat"] = float(value)
                    except ValueError:
                        pass
                elif "portion" in lower_line:
                    result["portion_size"] = line.split(':')[-1].strip()
                    
            elif current_section == "health_benefits":
                if line.startswith('-') or line.startswith('•'):
                    result["health_benefits"].append(line.lstrip('- •').strip())
                
            elif current_section == "concerns":
                if line.startswith('-') or line.startswith('•'):
                    result["concerns"].append(line.lstrip('- •').strip())
                
            elif current_section == "serving_suggestions":
                if line.startswith('-') or line.startswith('•'):
                    result["serving_suggestions"].append(line.lstrip('- •').strip())

        return result
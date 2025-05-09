import logging
import httpx
from openai import OpenAI
from tavily import TavilyClient
from com.mhire.app.config.config import Config
from com.mhire.app.services.workout_planner.workout_planner_schema import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkoutPlanner:
    def __init__(self):
        config = Config()
        self.openai_client = OpenAI(api_key=config.openai_api_key)
        self.model = config.model_name
        self.tavily_client = TavilyClient(api_key=config.tavily_api_key)
        self.tavily_api_key = config.tavily_api_key
        
    async def generate_workout_plan(self, profile: UserProfileRequest) -> WorkoutResponse:
        try:
            # Consider all profile aspects when creating workout structure
            workout_structure = self._create_workout_structure(profile)
            daily_workouts = []
            
            for day_num in range(3):
                focus = workout_structure["splits"][day_num % len(workout_structure["splits"])]
                daily_workout = await self._generate_daily_workout(profile, focus, day_num + 1)
                daily_workouts.append(daily_workout)
            
            return WorkoutResponse(
                success=True,
                workout_plan=daily_workouts,
                error=None
            )
        except Exception as e:
            logger.error(f"Error generating workout plan: {str(e)}")
            return WorkoutResponse(
                success=False,
                workout_plan=[],  # Empty list instead of None
                error=str(e)
            )

    def _create_workout_structure(self, profile: UserProfileRequest) -> dict:
        # Base structure based on primary goal
        base_structures = {
            PrimaryGoal.BUILD_MUSCLE: {
                "splits": ["Upper Body Push", "Lower Body", "Upper Body Pull"],
                "intensity": "High",
                "rest": "60-90s"
            },
            PrimaryGoal.LOSE_WEIGHT: {
                "splits": ["HIIT Cardio", "Full Body Strength", "Metabolic Conditioning"],
                "intensity": "Moderate-High",
                "rest": "30-45s"
            },
            PrimaryGoal.EAT_HEALTHIER: {
                "splits": ["Full Body", "Mobility & Flexibility", "Light Cardio"],
                "intensity": "Moderate",
                "rest": "45-60s"
            }
        }
        
        structure = base_structures.get(profile.primary_goal)
        
        # Adjust based on dietary profile
        if profile.eating_style == EatingStyle.VEGAN or profile.eating_style == EatingStyle.VEGETARIAN:
            structure["nutrition_note"] = "Include pre-workout protein sources"
            
        # Adjust based on energy levels
        if profile.caffeine_consumption == ConsumptionFrequency.NONE:
            structure["warm_up_duration"] = "15-20 minutes"  # Longer warm-up
        
        return structure

    async def _search_tavily_video(self, query: str) -> Optional[str]:
        """Search for exercise videos using Tavily API"""
        try:
            logging.info(f"Searching for video: {query}")
            
            # Using the official Tavily client library
            search_result = self.tavily_client.search(
                query=f"{query} exercise video tutorial demonstration",
                search_depth="advanced",
                include_domains=["youtube.com"],
                max_results=5
            )
            
            if search_result and search_result.get("results"):
                # Filter for YouTube videos
                videos = [r for r in search_result["results"] if "youtube.com" in r.get("url", "")]
                if videos:
                    video_url = videos[0]["url"]
                    logging.info(f"Found video: {video_url}")
                    return video_url
                
            logging.warning(f"No suitable video found for: {query}")
            return None
                
        except Exception as e:
            logging.error(f"Tavily API error for {query}: {str(e)}")
            return None

    async def _get_ai_response(self, prompt: str) -> str:
        """Get workout plan from OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional fitness coach creating detailed workout plans."},
                    {"role": "user", "content": prompt}
                ]
                # Removed temperature parameter as it's not supported
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    async def _generate_daily_workout(self, profile: UserProfileRequest, focus: str, day: int) -> DailyWorkout:
        try:
            # Get AI-generated workout content
            prompt = self._create_workout_prompt(profile, focus, day)
            workout_content = await self._get_ai_response(prompt)
            
            # Search for demonstration videos
            warm_up_video = await self._search_tavily_video(f"{focus} warm up exercises")
            main_video = await self._search_tavily_video(f"{focus} {profile.primary_goal} workout")
            cool_down_video = await self._search_tavily_video(f"{focus} cool down stretches")
            
            # Parse the workout data
            workout_data = self._parse_workout_response(workout_content)
            
            return DailyWorkout(
                day=f"Day {day}",
                focus=focus,
                warm_up=WorkoutSegment(
                    motto="Keep moving—you've got this.",
                    exercises=workout_data["warm_up"],
                    duration="10-15 minutes",
                    video_url=warm_up_video
                ),
                main_routine=WorkoutSegment(
                    motto="You're doing awesome—keep the energy up.",
                    exercises=workout_data["main_routine"],
                    duration="30-45 minutes",
                    video_url=main_video
                ),
                cool_down=WorkoutSegment(
                    motto="Breathe in peace—breathe out strength.",
                    exercises=workout_data["cool_down"],
                    duration="10-15 minutes",
                    video_url=cool_down_video
                )
            )
        except Exception as e:
            logger.error(f"Error generating daily workout: {str(e)}")
            raise

    def _create_workout_prompt(self, profile: UserProfileRequest, focus: str, day: int) -> str:
        return f"""Create a detailed {focus} workout for Day {day} considering:
        User Profile:
        - Primary Goal: {profile.primary_goal}
        - Weight: {profile.weight_kg}kg
        - Height: {profile.height_cm}cm
        - Diet: {profile.eating_style}
        - Meat Eater: {profile.is_meat_eater}
        - Lactose Intolerant: {profile.is_lactose_intolerant}
        - Allergies: {', '.join(profile.allergies)}
        - Caffeine: {profile.caffeine_consumption}
        - Sugar: {profile.sugar_consumption}

        Provide the workout plan in this format:
        
        Warm-up:
        - [Exercise Name] | [Instructions]
        - [Exercise Name] | [Instructions]
        
        Main Routine:
        - [Exercise Name] | Sets: [X] | Reps: [X] | Rest: [Xs] | [Instructions]
        - [Exercise Name] | Sets: [X] | Reps: [X] | Rest: [Xs] | [Instructions]
        
        Cool-down:
        - [Exercise Name] | [Instructions]
        - [Exercise Name] | [Instructions]
        """

    def _parse_workout_response(self, content: str) -> dict:
        """Parse the AI-generated workout content into structured segments"""
        segments = {
            "warm_up": [],
            "main_routine": [],
            "cool_down": []
        }
        current_section = None
        
        try:
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            for line in lines:
                lower_line = line.lower()
                
                # Detect section headers
                if "warm-up:" in lower_line or "warmup:" in lower_line:
                    current_section = "warm_up"
                    continue
                elif "main routine:" in lower_line or "main workout:" in lower_line:
                    current_section = "main_routine"
                    continue
                elif "cool-down:" in lower_line or "cooldown:" in lower_line:
                    current_section = "cool_down"
                    continue
                
                # Skip lines that don't start with bullet point or dash
                if not line.lstrip().startswith(('-', '•', '*')):
                    continue
                
                # Only process if we're in a valid section
                if current_section:
                    try:
                        # Split on pipe and clean up each part
                        parts = [p.strip() for p in line.lstrip('- •*').split('|')]
                        
                        # Extract exercise name (required)
                        name = parts[0].strip() if parts else "Unnamed Exercise"
                        
                        if current_section == "main_routine":
                            # Parse main routine with more detailed info
                            exercise_data = {
                                'sets': '3',  # Default values
                                'reps': '10-12',
                                'rest': '60s',
                                'instructions': ''
                            }
                            
                            # Process each part looking for specific keywords
                            for part in parts[1:]:
                                part = part.lower().strip()
                                if 'sets:' in part:
                                    sets_str = ''.join(filter(str.isdigit, part))
                                    exercise_data['sets'] = sets_str if sets_str else '3'
                                elif 'reps:' in part:
                                    exercise_data['reps'] = part.split(':')[-1].strip()
                                elif 'rest:' in part:
                                    exercise_data['rest'] = part.split(':')[-1].strip()
                                else:
                                    exercise_data['instructions'] = part
                            
                            # Create exercise with extracted or default values
                            exercise = Exercise(
                                name=name,
                                sets=int(exercise_data['sets']),
                                reps=exercise_data['reps'],
                                rest=exercise_data['rest'],
                                instructions=exercise_data['instructions']
                            )
                        else:
                            # Simpler parsing for warm-up and cool-down
                            instructions = parts[1].strip() if len(parts) > 1 else "Perform at a comfortable pace"
                            exercise = Exercise(
                                name=name,
                                sets=1,
                                reps="As needed",
                                rest="None",
                                instructions=instructions
                            )
                        
                        segments[current_section].append(exercise)
                    except Exception as e:
                        logger.warning(f"Error parsing exercise line '{line}': {str(e)}")
                        # Continue with next line instead of failing completely
                        continue
            
            # Ensure each section has at least one exercise
            for section in segments:
                if not segments[section]:
                    segments[section].append(Exercise(
                        name=f"Basic {section.replace('_', ' ').title()}",
                        sets=1,
                        reps="As needed",
                        rest="None",
                        instructions="Perform at a comfortable pace"
                    ))
            
            return segments
            
        except Exception as e:
            logger.error(f"Error parsing workout response: {str(e)}")
            # Return a minimal valid structure rather than failing
            return {
                section: [Exercise(
                    name=f"Basic {section.replace('_', ' ').title()}",
                    sets=1,
                    reps="As needed",
                    rest="None",
                    instructions="Perform at a comfortable pace"
                )] for section in ["warm_up", "main_routine", "cool_down"]
            }
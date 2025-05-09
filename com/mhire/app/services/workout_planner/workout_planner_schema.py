from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class PrimaryGoal(str, Enum):
    BUILD_MUSCLE = "Build muscle"
    LOSE_WEIGHT = "Lose weight"
    EAT_HEALTHIER = "Eat healthier"

class EatingStyle(str, Enum):
    VEGAN = "Vegan"
    KETO = "Keto"
    PALEO = "Paleo"
    VEGETARIAN = "Vegetarian"
    BALANCED = "Balanced"
    NONE = "None"

class ConsumptionFrequency(str, Enum):
    NONE = "None"
    OCCASIONALLY = "Occasionally"
    REGULARLY = "Regularly"
    CRAVINGS = "Cravings"

class UserProfileRequest(BaseModel):
    primary_goal: PrimaryGoal
    weight_kg: float
    height_cm: float
    is_meat_eater: bool
    is_lactose_intolerant: bool
    allergies: List[str]
    eating_style: EatingStyle
    caffeine_consumption: ConsumptionFrequency
    sugar_consumption: ConsumptionFrequency

# Workout specific response models
class Exercise(BaseModel):
    name: str
    sets: int
    reps: str
    rest: str
    instructions: str

class WorkoutSegment(BaseModel):
    motto: str
    exercises: List[Exercise]
    duration: str
    video_url: Optional[str]

class DailyWorkout(BaseModel):
    day: str
    focus: str
    warm_up: WorkoutSegment
    main_routine: WorkoutSegment
    cool_down: WorkoutSegment

class WorkoutResponse(BaseModel):
    success: bool = True
    workout_plan: List[DailyWorkout] = []  # Changed to required field with default empty list
    error: Optional[str] = None
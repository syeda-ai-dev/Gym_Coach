from pydantic import BaseModel
from typing import List
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

class UserProfile(BaseModel):
    primary_goal: PrimaryGoal
    weight_kg: float
    height_cm: float
    is_meat_eater: bool
    is_lactose_intolerant: bool
    allergies: List[str]
    eating_style: EatingStyle
    caffeine_consumption: ConsumptionFrequency
    sugar_consumption: ConsumptionFrequency

class Meal(BaseModel):
    name: str
    description: str
    calories: float
    protein: float
    carbs: float
    fat: float
    rationale: str
    preparation_steps: List[str]

class DailyMealPlan(BaseModel):
    breakfast: Meal
    lunch: Meal
    snack: Meal
    dinner: Meal
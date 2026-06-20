from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class DetectedFood(BaseModel):
    name: str
    confidence: float
    display_name: str


class AnalyzeImageResponse(BaseModel):
    foods: List[DetectedFood]
    image_url: str
    session_id: str


class GenerateQuestionsRequest(BaseModel):
    session_id: str
    foods: List[str]


class Question(BaseModel):
    id: str
    question: str
    options: List[str]
    food_name: str


class QuestionsResponse(BaseModel):
    questions: List[Question]
    session_id: str


class CalculateNutritionRequest(BaseModel):
    session_id: str
    answers: Dict[str, str]


class Micronutrients(BaseModel):
    calcium_mg: float = 0
    iron_mg: float = 0
    vitamin_c_mg: float = 0
    potassium_mg: float = 0
    sodium_mg: float = 0
    vitamin_a_ug: float = 0


class HealthScores(BaseModel):
    weight_loss: int = 0
    muscle_gain: int = 0
    diabetic_friendly: int = 0
    heart_health: int = 0
    overall: int = 0


class NutritionResult(BaseModel):
    meal_id: str
    foods: List[str]
    total_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    micronutrients: Micronutrients
    health_scores: HealthScores
    image_url: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class MealSummary(BaseModel):
    meal_id: str
    foods: List[str]
    total_calories: float
    protein_g: float
    image_url: Optional[str]
    created_at: str


class MealHistory(BaseModel):
    meals: List[MealSummary]
    total: int


class DailyData(BaseModel):
    date: str
    calories: float
    protein: float


class TopFood(BaseModel):
    name: str
    count: int


class DashboardData(BaseModel):
    today_calories: float
    today_protein: float
    today_carbs: float
    today_fat: float
    calorie_goal: int
    weekly_data: List[DailyData]
    top_foods: List[TopFood]


class ManualAnalyzeRequest(BaseModel):
    food_names: List[str]


class FoodMatch(BaseModel):
    input_name: str
    matched: bool
    indb_name: Optional[str] = None


class ManualAnalyzeResponse(BaseModel):
    foods: List[DetectedFood]
    image_url: str
    session_id: str
    matches: List[FoodMatch]

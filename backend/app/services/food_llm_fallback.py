"""
LLM Food Recognition Fallback
When a food is not found in the database, use LLM to:
1. Identify what the food is
2. Find closest match in database
3. Estimate nutrition if no match found
"""
import json
import re
from typing import Optional, Dict
from openai import OpenAI
from app.config import settings


# Initialize OpenRouter client (reuse existing config)
_client = OpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)

RECOGNITION_PROMPT = """You are a nutrition expert specializing in Indian cuisine. A user submitted an unrecognized food item.

Food name entered: "{food_name}"

Your task:
1. Identify what this food likely is
2. Provide canonical name (standardized English name used in nutrition databases)
3. Estimate nutritional values per 100g if you can recognize it
4. Return ONLY valid JSON, no markdown:

{{
  "canonical_name": "Standardized food name (e.g., 'Masala Dosa', 'Idli')",
  "food_type": "grain | protein | vegetable | fruit | snack | beverage | other",
  "serving_unit": "g | piece | cup | bowl",
  "recognized": true,
  "energy_kcal": 150.0,
  "protein_g": 5.0,
  "carb_g": 25.0,
  "fat_g": 3.0,
  "fiber_g": 2.0,
  "confidence": 0.85,
  "notes": "Brief description of what this food is"
}}

Be conservative with nutrition estimates. If unsure, mark "recognized": false and provide best guess."""


async def fallback_food_recognition(food_name: str) -> Optional[Dict]:
    """
    Use LLM to recognize and estimate nutrition for unrecognized foods.
    Returns dict with canonical_name, nutrition, confidence, or None if LLM fails.
    """
    try:
        prompt = RECOGNITION_PROMPT.format(food_name=food_name)

        response = await _call_llm_async(prompt)
        if not response:
            return None

        # Parse JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            return None

        data = json.loads(json_match.group())

        # Validate required fields
        required = ["canonical_name", "energy_kcal", "protein_g", "carb_g", "fat_g", "confidence"]
        if not all(k in data for k in required):
            return None

        return {
            "canonical_name": str(data.get("canonical_name", food_name)),
            "food_type": str(data.get("food_type", "other")),
            "serving_unit": str(data.get("serving_unit", "g")),
            "recognized": bool(data.get("recognized", True)),
            "energy_kcal": float(data.get("energy_kcal", 0)),
            "protein_g": float(data.get("protein_g", 0)),
            "carb_g": float(data.get("carb_g", 0)),
            "fat_g": float(data.get("fat_g", 0)),
            "fiber_g": float(data.get("fiber_g", 0)),
            "confidence": float(data.get("confidence", 0.5)),
            "notes": str(data.get("notes", "")),
            "source": "llm_estimated",  # Mark as LLM-generated
        }

    except Exception as e:
        print(f"[LLM Food Fallback] Error: {e}")
        return None


def _call_llm_sync(prompt: str) -> Optional[str]:
    """Synchronous LLM call (for blocking contexts)."""
    try:
        response = _client.chat.completions.create(
            model=settings.llm_report_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Low temp for factual nutrition info
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM Food Fallback Sync] Error: {e}")
        return None


async def _call_llm_async(prompt: str) -> Optional[str]:
    """Asynchronous LLM call."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _call_llm_sync(prompt))


def fallback_food_recognition_sync(food_name: str) -> Optional[Dict]:
    """Synchronous version of fallback_food_recognition (for non-async contexts)."""
    try:
        prompt = RECOGNITION_PROMPT.format(food_name=food_name)
        response = _call_llm_sync(prompt)

        if not response:
            return None

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            return None

        data = json.loads(json_match.group())

        required = ["canonical_name", "energy_kcal", "protein_g", "carb_g", "fat_g", "confidence"]
        if not all(k in data for k in required):
            return None

        return {
            "canonical_name": str(data.get("canonical_name", food_name)),
            "food_type": str(data.get("food_type", "other")),
            "serving_unit": str(data.get("serving_unit", "g")),
            "recognized": bool(data.get("recognized", True)),
            "energy_kcal": float(data.get("energy_kcal", 0)),
            "protein_g": float(data.get("protein_g", 0)),
            "carb_g": float(data.get("carb_g", 0)),
            "fat_g": float(data.get("fat_g", 0)),
            "fiber_g": float(data.get("fiber_g", 0)),
            "confidence": float(data.get("confidence", 0.5)),
            "notes": str(data.get("notes", "")),
            "source": "llm_estimated",
        }

    except Exception as e:
        print(f"[LLM Food Fallback] Error: {e}")
        return None

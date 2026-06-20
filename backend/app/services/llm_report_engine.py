"""
LLM-powered report engine using OpenRouter.
Analyzes a user's complete 7-day challenge data to:
  1. Assess how serious they are about their health transformation
  2. Recommend specific Indian foods tailored to their pattern gaps
"""
import asyncio
import json
import re
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from app.config import settings


def _format_audit(audit: Any) -> str:
    if not audit or not audit.completed:
        return "Lifestyle audit not completed."
    lines = []
    if audit.city:
        lines.append(f"City: {audit.city}")
    if audit.occupation:
        lines.append(f"Occupation: {audit.occupation}")
    if audit.cooking_at_home is not None:
        lines.append(f"Cooks at home: {'yes' if audit.cooking_at_home else 'no'}")
    if audit.sleep_hours:
        lines.append(f"Sleep: {audit.sleep_hours} hrs/night, quality: {audit.sleep_quality or 'not specified'}")
    if audit.wake_time:
        lines.append(f"Wake time: {audit.wake_time}")
    if audit.meals_per_day:
        lines.append(f"Meals per day: {audit.meals_per_day}")
    if audit.breakfast_habit:
        lines.append(f"Breakfast habit: {audit.breakfast_habit}")
    if audit.water_intake:
        lines.append(f"Water intake: {audit.water_intake}")
    if audit.outside_food_frequency:
        lines.append(f"Outside food frequency: {audit.outside_food_frequency}")
    if audit.sugary_beverage_frequency:
        lines.append(f"Sugary beverage frequency: {audit.sugary_beverage_frequency}")
    if audit.processed_food_frequency:
        lines.append(f"Processed food frequency: {audit.processed_food_frequency}")
    if audit.activity_level:
        lines.append(f"Activity level: {audit.activity_level}")
    if audit.exercise_frequency:
        lines.append(f"Exercise frequency: {audit.exercise_frequency}")
    if audit.stress_level:
        lines.append(f"Stress level: {audit.stress_level}")
    if audit.stress_eating:
        lines.append(f"Stress eating: {audit.stress_eating}")
    if audit.digestion_issues:
        lines.append(f"Digestion issues: yes — {audit.digestion_notes or 'no details'}")
    if audit.bowel_regularity:
        lines.append(f"Bowel regularity: {audit.bowel_regularity}")
    if audit.health_goals:
        lines.append(f"Stated health goals: {audit.health_goals}")
    if audit.dietary_restrictions:
        lines.append(f"Dietary restrictions: {audit.dietary_restrictions}")
    return "\n".join(lines)


def _format_meal_logs(meal_logs: List[Any]) -> str:
    by_day: Dict[int, List[Any]] = {}
    for log in meal_logs:
        by_day.setdefault(log.day_number, []).append(log)

    lines = []
    for day in sorted(by_day):
        lines.append(f"Day {day}:")
        for log in sorted(by_day[day], key=lambda x: x.meal_type):
            tags = ", ".join(log.food_pattern_tags or []) or "no tags"
            text = log.meal_text or "(no description)"
            lines.append(f"  {log.meal_type}: {text}  [Tags: {tags}]")
        if day not in by_day:
            lines.append(f"Day {day}: SKIPPED")

    for missing_day in range(1, 8):
        if missing_day not in by_day:
            lines.append(f"Day {missing_day}: SKIPPED — no meals submitted")

    return "\n".join(lines)


def _build_prompt(
    client: Any,
    audit: Optional[Any],
    meal_logs: List[Any],
    food_pattern_pct: Dict[str, float],
    compliance_pct: float,
    completed_days: int,
    avg_daily_calories: float,
    avg_daily_protein: float,
) -> str:
    # Profile section
    profile_lines = [f"Name: {client.name}"]
    if client.age:
        profile_lines.append(f"Age: {client.age}")
    if client.gender:
        profile_lines.append(f"Gender: {client.gender}")
    if getattr(client, "height_cm", None):
        profile_lines.append(f"Height: {client.height_cm} cm")
    if getattr(client, "weight_kg", None):
        profile_lines.append(f"Weight: {client.weight_kg} kg")
    if client.goal:
        profile_lines.append(f"Health goal: {client.goal}")

    # Food pattern section
    pattern_lines = [
        f"- {k}: {v:.0f}% of meals"
        for k, v in sorted(food_pattern_pct.items())
    ]

    prompt = f"""You are a certified nutritionist and wellness coach specializing in Indian food patterns and holistic health transformation.

Analyze the complete 7-day challenge data below and produce a structured JSON report.

=== USER PROFILE ===
{chr(10).join(profile_lines)}

=== LIFESTYLE AUDIT ===
{_format_audit(audit)}

=== CHALLENGE PERFORMANCE ===
- Days completed (all 3 meals submitted): {completed_days}/7
- Compliance score: {compliance_pct:.1f}%
- Average daily calories: {avg_daily_calories:.0f} kcal
- Average daily protein: {avg_daily_protein:.1f} g

=== FOOD PATTERN ANALYSIS ===
{chr(10).join(pattern_lines) or "No pattern data available."}

=== DAILY MEAL LOGS ===
{_format_meal_logs(meal_logs)}

=== INSTRUCTIONS ===
Based on ALL the above data, return ONLY a valid JSON object with exactly these keys:

{{
  "commitment_level": "HIGH" or "MODERATE" or "LOW",
  "commitment_analysis": "3-4 sentences. Honest, warm assessment of whether this person is truly serious about transformation. Look at: days skipped, food quality choices (processed vs whole), audit answers about stress eating / outside food / sleep, and whether actual meals aligned with their stated goal. Be direct but encouraging.",
  "seriousness_indicators": [
    "4-6 specific behavioral facts from their data — both positive signals and red flags. Each must reference an actual data point."
  ],
  "food_recommendations": [
    {{
      "food_name": "Specific Indian food name",
      "category": "grain | protein | vegetable | fruit | beverage | snack",
      "reason": "Why this food addresses THIS user's specific gap — reference their pattern % or audit answer",
      "when_to_eat": "breakfast | mid-morning | lunch | evening snack | dinner",
      "how_to_prepare": "One practical sentence. Match their home-cooking habit from audit."
    }}
  ],
  "llm_summary": "4-5 sentences. Warm narrative of their 7-day journey. What they did well, what the data reveals about their relationship with food, and one forward-looking encouragement. Use their name.",
  "personalized_insights": [
    "4-6 specific, data-driven insights about this user's unique food patterns and lifestyle factors. Each must cite actual numbers or behaviors from the logs or audit."
  ]
}}

Rules for food_recommendations (must have 5-7 items):
- If PROTEIN_PRESENT < 50%: recommend dal, eggs, paneer, or curd
- If VEGETABLE_PRESENT < 50%: recommend a specific sabzi or soup
- If FRUIT_PRESENT < 40%: recommend a seasonal fruit as snack
- If FIBER_SOURCE < 30%: recommend ragi, oats, or whole grain
- If SUGARY_BEVERAGE > 40%: recommend herbal tea or buttermilk as replacement
- If PROCESSED_FOOD > 30%: recommend a homemade snack alternative
- Always include at least one traditional South/North Indian food that fits their pattern
- If they cook at home (from audit), give home-prep instructions; if they eat out, suggest what to order

Commitment level guide:
- HIGH: 6-7 days completed + low processed food + meals aligned with goal
- MODERATE: 4-6 days completed OR moderate processed food
- LOW: <4 days completed OR high processed/sugary pattern despite stated transformation goal

Return ONLY the JSON. No markdown fences, no explanation."""

    return prompt


async def generate_llm_report(
    client: Any,
    audit: Optional[Any],
    meal_logs: List[Any],
    food_pattern_pct: Dict[str, float],
    compliance_pct: float,
    completed_days: int,
    avg_daily_calories: float,
    avg_daily_protein: float,
) -> Dict:
    prompt = _build_prompt(
        client=client,
        audit=audit,
        meal_logs=meal_logs,
        food_pattern_pct=food_pattern_pct,
        compliance_pct=compliance_pct,
        completed_days=completed_days,
        avg_daily_calories=avg_daily_calories,
        avg_daily_protein=avg_daily_protein,
    )

    or_client = AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    try:
        response = await or_client.chat.completions.create(
            model=settings.llm_report_model,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content.strip()

        # Strip optional markdown fences
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"[LLM report] generation failed: {e}")

    return _fallback_report(client.name, compliance_pct, completed_days, food_pattern_pct)


def _fallback_report(
    name: str,
    compliance_pct: float,
    completed_days: int,
    pct: Dict[str, float],
) -> Dict:
    if compliance_pct >= 85 and pct.get("PROCESSED_FOOD", 100) < 30:
        level = "HIGH"
    elif compliance_pct >= 57:
        level = "MODERATE"
    else:
        level = "LOW"

    recommendations = []
    if pct.get("PROTEIN_PRESENT", 0) < 50:
        recommendations.append({
            "food_name": "Moong Dal",
            "category": "protein",
            "reason": f"Protein was present in only {pct.get('PROTEIN_PRESENT', 0):.0f}% of meals — moong dal is easy to digest and rich in plant protein.",
            "when_to_eat": "lunch",
            "how_to_prepare": "Pressure-cook with turmeric and temper with cumin and mustard seeds.",
        })
    if pct.get("VEGETABLE_PRESENT", 0) < 50:
        recommendations.append({
            "food_name": "Palak Sabzi",
            "category": "vegetable",
            "reason": f"Vegetables appeared in only {pct.get('VEGETABLE_PRESENT', 0):.0f}% of meals — spinach is iron-rich and quick to cook.",
            "when_to_eat": "dinner",
            "how_to_prepare": "Stir-fry with garlic, a pinch of cumin, and minimal oil.",
        })
    if pct.get("FRUIT_PRESENT", 0) < 40:
        recommendations.append({
            "food_name": "Banana",
            "category": "fruit",
            "reason": "Fruit was nearly absent — one banana provides natural sugars, potassium, and fiber.",
            "when_to_eat": "mid-morning",
            "how_to_prepare": "Eat fresh or blend into a small smoothie with curd.",
        })
    if pct.get("FIBER_SOURCE", 0) < 30:
        recommendations.append({
            "food_name": "Ragi Mudde",
            "category": "grain",
            "reason": f"Fiber sources appeared in only {pct.get('FIBER_SOURCE', 0):.0f}% of meals — ragi is a high-fiber millet ideal for South Indian diets.",
            "when_to_eat": "dinner",
            "how_to_prepare": "Cook as thick porridge or mudde balls; pair with sambar.",
        })
    if pct.get("SUGARY_BEVERAGE", 0) > 40:
        recommendations.append({
            "food_name": "Spiced Buttermilk",
            "category": "beverage",
            "reason": f"Sugary beverages appeared in {pct.get('SUGARY_BEVERAGE', 0):.0f}% of meals — buttermilk provides probiotics and hydration without added sugar.",
            "when_to_eat": "after lunch",
            "how_to_prepare": "Blend curd with water, rock salt, curry leaves, and a pinch of asafoetida.",
        })
    if pct.get("PROCESSED_FOOD", 0) > 30:
        recommendations.append({
            "food_name": "Roasted Chana",
            "category": "snack",
            "reason": f"Processed food appeared in {pct.get('PROCESSED_FOOD', 0):.0f}% of meals — roasted chana is a high-protein, high-fiber packaged-snack replacement.",
            "when_to_eat": "evening snack",
            "how_to_prepare": "Buy pre-roasted or dry-roast at home with salt and chili powder.",
        })
    if len(recommendations) < 5:
        recommendations.append({
            "food_name": "Idli with Sambar",
            "category": "grain",
            "reason": "Traditional Indian meal that is balanced in carbs and protein, easy to digest.",
            "when_to_eat": "breakfast",
            "how_to_prepare": "Steam idlis from fermented batter; pair with vegetable-rich sambar.",
        })

    return {
        "commitment_level": level,
        "commitment_analysis": (
            f"{name} completed {completed_days} out of 7 days with a {compliance_pct:.0f}% compliance score. "
            f"Their food choices suggest a {level.lower()} level of commitment to their wellness journey. "
            "Consistent daily meals are the strongest signal of serious intent, and this data helps identify where to focus next."
        ),
        "seriousness_indicators": [
            f"Completed {completed_days}/7 days of the challenge",
            f"Protein present in {pct.get('PROTEIN_PRESENT', 0):.0f}% of meals",
            f"Vegetables present in {pct.get('VEGETABLE_PRESENT', 0):.0f}% of meals",
            f"Traditional foods in {pct.get('TRADITIONAL_FOOD', 0):.0f}% of meals",
            f"Processed food in {pct.get('PROCESSED_FOOD', 0):.0f}% of meals",
        ],
        "food_recommendations": recommendations,
        "llm_summary": (
            f"{name} has completed the 7-Day Wholesome Eating Challenge with {compliance_pct:.0f}% compliance. "
            f"Their food patterns reveal a foundation of traditional Indian eating with opportunities to strengthen protein and vegetable intake. "
            "Consistent small improvements — one food swap at a time — will accelerate their transformation journey."
        ),
        "personalized_insights": [
            f"Protein was present in {pct.get('PROTEIN_PRESENT', 0):.0f}% of meals — targeting 70%+ would improve satiety and energy.",
            f"Traditional foods appeared in {pct.get('TRADITIONAL_FOOD', 0):.0f}% of meals — a strong cultural foundation for sustained healthy eating.",
            f"Balanced meals (protein + vegetable, no processed food) made up {pct.get('BALANCED_MEAL', 0):.0f}% of submissions.",
        ],
    }

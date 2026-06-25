"""
Seed all 35 lifestyle audit questions from the Sarvarasa specification.
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.lifestyle_audit import Base, LifestyleAuditQuestion
from app.config import settings

QUESTIONS = [
    # Section B - Sleep (Q7-Q12)
    {
        "section": "B",
        "number": 7,
        "text": "What time do you usually go to sleep on weeknights?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Before 10 PM"},
            {"label": "B", "value": "B", "text": "10 PM to 11 PM"},
            {"label": "C", "value": "C", "text": "11 PM to midnight"},
            {"label": "D", "value": "D", "text": "Midnight to 1 AM"},
            {"label": "E", "value": "E", "text": "After 1 AM"},
        ],
        "weight": 1.5,
    },
    {
        "section": "B",
        "number": 8,
        "text": "What time do you usually wake up?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Before 6 AM"},
            {"label": "B", "value": "B", "text": "6 AM to 7 AM"},
            {"label": "C", "value": "C", "text": "7 AM to 8 AM"},
            {"label": "D", "value": "D", "text": "After 8 AM"},
            {"label": "E", "value": "E", "text": "I have no fixed wake time — it depends on the day"},
        ],
        "weight": 1.5,
    },
    {
        "section": "B",
        "number": 9,
        "text": "On most nights, how many hours of actual sleep do you get?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "7 to 9 hours"},
            {"label": "B", "value": "B", "text": "6 to 7 hours"},
            {"label": "C", "value": "C", "text": "5 to 6 hours"},
            {"label": "D", "value": "D", "text": "Less than 5 hours"},
            {"label": "E", "value": "E", "text": "It varies a lot — I cannot predict it"},
        ],
        "weight": 1.5,
    },
    {
        "section": "B",
        "number": 10,
        "text": "When you wake up, how do you feel?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Rested and ready — I feel okay getting up"},
            {"label": "B", "value": "B", "text": "Groggy for 10 to 15 minutes but okay after that"},
            {"label": "C", "value": "C", "text": "Tired — I want to sleep more and often hit snooze"},
            {"label": "D", "value": "D", "text": "Heavy and exhausted — mornings are hard"},
            {"label": "E", "value": "E", "text": "I never feel rested, regardless of how long I sleep"},
        ],
        "weight": 1.5,
    },
    {
        "section": "B",
        "number": 11,
        "text": "What do you usually do in the last 30 minutes before sleeping?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "I avoid screens — I read, meditate, or wind down quietly"},
            {"label": "B", "value": "B", "text": "I use my phone occasionally but stop before I sleep"},
            {"label": "C", "value": "C", "text": "I scroll social media or watch content until I feel sleepy"},
            {"label": "D", "value": "D", "text": "I am on my phone or a screen right until I fall asleep"},
            {"label": "E", "value": "E", "text": "I often fall asleep while watching something"},
        ],
        "weight": 1.5,
    },
    {
        "section": "B",
        "number": 12,
        "text": "How often do you have difficulty falling asleep?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Never — I fall asleep easily"},
            {"label": "B", "value": "B", "text": "Rarely — only occasionally"},
            {"label": "C", "value": "C", "text": "Sometimes — a few nights a week"},
            {"label": "D", "value": "D", "text": "Often — most nights"},
            {"label": "E", "value": "E", "text": "Almost every night"},
        ],
        "weight": 1.5,
    },
    # Section C - Food & Eating (Q13-Q20)
    {
        "section": "C",
        "number": 13,
        "text": "How many proper meals do you eat on a typical weekday? (Not counting tea, coffee, or small snacks)",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "3 or more meals at roughly consistent times"},
            {"label": "B", "value": "B", "text": "2 proper meals, fairly consistent"},
            {"label": "C", "value": "C", "text": "2 proper meals but timing varies a lot"},
            {"label": "D", "value": "D", "text": "1 proper meal most days"},
            {"label": "E", "value": "E", "text": "I eat whenever I get time — no real pattern"},
        ],
        "weight": 1.5,
    },
    {
        "section": "C",
        "number": 14,
        "text": "Are your meal timings regular or irregular?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Very regular — roughly same time every day"},
            {"label": "B", "value": "B", "text": "Usually regular with occasional variation"},
            {"label": "C", "value": "C", "text": "Irregular — timing shifts by hours depending on work"},
            {"label": "D", "value": "D", "text": "Very irregular — no consistent timing at all"},
        ],
        "weight": 1.5,
    },
    {
        "section": "C",
        "number": 15,
        "text": "What time do you usually finish dinner?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Before 7:30 PM most days"},
            {"label": "B", "value": "B", "text": "7:30 PM to 8:30 PM most days"},
            {"label": "C", "value": "C", "text": "8:30 PM to 9:30 PM most days"},
            {"label": "D", "value": "D", "text": "After 9:30 PM most days"},
            {"label": "E", "value": "E", "text": "After 10:30 PM most days"},
        ],
        "weight": 1.5,
    },
    {
        "section": "C",
        "number": 16,
        "text": "How often do you eat junk or processed food in a typical week?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Rarely — once a month or less"},
            {"label": "B", "value": "B", "text": "Occasionally — once or twice a week"},
            {"label": "C", "value": "C", "text": "Often — 3 to 4 times a week"},
            {"label": "D", "value": "D", "text": "Most days"},
            {"label": "E", "value": "E", "text": "Almost every meal includes processed or outside food"},
        ],
        "weight": 1.5,
    },
    {
        "section": "C",
        "number": 17,
        "text": "How often do you eat after 9 PM or late at night?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Rarely — almost never"},
            {"label": "B", "value": "B", "text": "Once or twice a week"},
            {"label": "C", "value": "C", "text": "3 to 4 nights a week"},
            {"label": "D", "value": "D", "text": "Most nights"},
            {"label": "E", "value": "E", "text": "Every night"},
        ],
        "weight": 1.5,
    },
    {
        "section": "C",
        "number": 18,
        "text": "How would you describe your sugar cravings?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Low — I rarely crave sweets or sugary food"},
            {"label": "B", "value": "B", "text": "Moderate — I crave occasionally and can manage it"},
            {"label": "C", "value": "C", "text": "High — I frequently crave and usually give in"},
            {"label": "D", "value": "D", "text": "Very high — I need something sweet most days"},
        ],
        "weight": 1.5,
    },
    {
        "section": "C",
        "number": 19,
        "text": "Do you eat differently when you are stressed, bored, or upset?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "No — my eating is not strongly linked to my mood"},
            {"label": "B", "value": "B", "text": "Sometimes — minor changes when stressed"},
            {"label": "C", "value": "C", "text": "Often — I eat more or reach for specific foods when stressed"},
            {"label": "D", "value": "D", "text": "Yes — food is my primary way of managing difficult emotions"},
        ],
        "weight": 1.5,
    },
    {
        "section": "C",
        "number": 20,
        "text": "How much water do you drink in a typical day?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "2 litres or more"},
            {"label": "B", "value": "B", "text": "1 to 2 litres"},
            {"label": "C", "value": "C", "text": "Less than 1 litre"},
            {"label": "D", "value": "D", "text": "I am not sure — I do not track it"},
        ],
        "weight": 1.5,
    },
    # Section D - Movement (Q21-Q25)
    {
        "section": "D",
        "number": 21,
        "text": "How many days per week do you do any intentional physical activity? (Walking, exercise, yoga, sports — anything purposeful)",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "5 or more days"},
            {"label": "B", "value": "B", "text": "3 to 4 days"},
            {"label": "C", "value": "C", "text": "1 to 2 days"},
            {"label": "D", "value": "D", "text": "Less than once a week"},
            {"label": "E", "value": "E", "text": "I do not do any intentional physical activity"},
        ],
        "weight": 1.0,
    },
    {
        "section": "D",
        "number": 22,
        "text": "On a typical day, how much do you walk in total?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "More than 30 minutes of walking"},
            {"label": "B", "value": "B", "text": "15 to 30 minutes"},
            {"label": "C", "value": "C", "text": "Less than 15 minutes"},
            {"label": "D", "value": "D", "text": "Minimal — I take vehicles or lifts for almost everything"},
        ],
        "weight": 1.0,
    },
    {
        "section": "D",
        "number": 23,
        "text": "How long do you sit continuously without getting up on a typical workday?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Rarely more than 1 hour without moving"},
            {"label": "B", "value": "B", "text": "1 to 2 hours at a stretch sometimes"},
            {"label": "C", "value": "C", "text": "2 to 3 hours regularly without a break"},
            {"label": "D", "value": "D", "text": "3 to 4 hours without getting up"},
            {"label": "E", "value": "E", "text": "4 or more hours without getting up"},
        ],
        "weight": 1.0,
    },
    {
        "section": "D",
        "number": 24,
        "text": "Do you experience any regular body pain or stiffness?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "No — my body feels fine generally"},
            {"label": "B", "value": "B", "text": "Occasional minor stiffness — usually in the morning"},
            {"label": "C", "value": "C", "text": "Regular lower back or neck pain from sitting"},
            {"label": "D", "value": "D", "text": "Daily pain or stiffness that affects how I move"},
        ],
        "weight": 1.0,
    },
    {
        "section": "D",
        "number": 25,
        "text": "How would you describe your energy levels during the day?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Consistently good — no significant dips"},
            {"label": "B", "value": "B", "text": "Good in the morning, slight dip in the afternoon"},
            {"label": "C", "value": "C", "text": "Noticeable afternoon crash — I need tea or coffee to recover"},
            {"label": "D", "value": "D", "text": "Low energy most of the day"},
            {"label": "E", "value": "E", "text": "Exhausted for most of the day regardless of sleep"},
        ],
        "weight": 1.0,
    },
    # Section E - Stress (Q26-Q30)
    {
        "section": "E",
        "number": 26,
        "text": "On a scale of 1 to 10, how would you rate your current stress level? (1 = very low, 10 = overwhelming)",
        "type": "scale",
        "options": [],
        "weight": 1.0,
    },
    {
        "section": "E",
        "number": 27,
        "text": "What is your biggest source of stress right now?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Work pressure — deadlines, performance, or relationships at work"},
            {"label": "B", "value": "B", "text": "Family or relationship situations"},
            {"label": "C", "value": "C", "text": "Financial concerns"},
            {"label": "D", "value": "D", "text": "Health concerns — my own or someone close to me"},
            {"label": "E", "value": "E", "text": "Multiple areas simultaneously"},
            {"label": "F", "value": "F", "text": "I am not under significant stress right now"},
        ],
        "weight": 1.0,
    },
    {
        "section": "E",
        "number": 28,
        "text": "How often do your mood or emotional state fluctuate significantly during the day?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Rarely — I am generally emotionally steady"},
            {"label": "B", "value": "B", "text": "Occasionally — minor fluctuations"},
            {"label": "C", "value": "C", "text": "Often — I notice significant shifts in mood most days"},
            {"label": "D", "value": "D", "text": "Very often — my mood is unpredictable and hard to manage"},
        ],
        "weight": 1.0,
    },
    {
        "section": "E",
        "number": 29,
        "text": "What is your primary motivation for joining this program?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "A specific health concern or doctor's advice"},
            {"label": "B", "value": "B", "text": "I want to lose weight and feel better in my body"},
            {"label": "C", "value": "C", "text": "I want more energy and better daily function"},
            {"label": "D", "value": "D", "text": "I want to build sustainable habits before problems start"},
            {"label": "E", "value": "E", "text": "Someone I know recommended it"},
        ],
        "weight": 1.0,
    },
    {
        "section": "E",
        "number": 30,
        "text": "What has been your biggest challenge in maintaining healthy habits in the past?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "I do not have enough time"},
            {"label": "B", "value": "B", "text": "I start but cannot stay consistent"},
            {"label": "C", "value": "C", "text": "I lack support or accountability"},
            {"label": "D", "value": "D", "text": "I find healthy food difficult to access or prepare"},
            {"label": "E", "value": "E", "text": "Stress and emotional state derail me"},
            {"label": "F", "value": "F", "text": "I have not seriously tried before"},
        ],
        "weight": 1.0,
    },
    # Section F - Digestion (Q31-Q35)
    {
        "section": "F",
        "number": 31,
        "text": "How often do you experience bloating or a feeling of fullness and discomfort after meals?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Rarely — only when I eat something unusual"},
            {"label": "B", "value": "B", "text": "Occasionally — once or twice a week"},
            {"label": "C", "value": "C", "text": "Often — several times a week"},
            {"label": "D", "value": "D", "text": "Most days"},
            {"label": "E", "value": "E", "text": "Almost every meal"},
        ],
        "weight": 1.5,
    },
    {
        "section": "F",
        "number": 32,
        "text": "How would you describe your bowel movement pattern?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Regular — once a day at roughly the same time"},
            {"label": "B", "value": "B", "text": "Mostly regular — once a day but timing varies"},
            {"label": "C", "value": "C", "text": "Once every 2 days or less frequently"},
            {"label": "D", "value": "D", "text": "Irregular — I cannot predict when"},
            {"label": "E", "value": "E", "text": "Constipation is a persistent concern for me"},
        ],
        "weight": 1.5,
    },
    {
        "section": "F",
        "number": 33,
        "text": "How often do you experience acidity, heartburn, or a burning sensation in your chest or stomach?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Never or very rarely"},
            {"label": "B", "value": "B", "text": "Once or twice a month"},
            {"label": "C", "value": "C", "text": "Once or twice a week"},
            {"label": "D", "value": "D", "text": "Most days"},
            {"label": "E", "value": "E", "text": "Multiple times per day"},
        ],
        "weight": 1.5,
    },
    {
        "section": "F",
        "number": 34,
        "text": "How would you describe your appetite?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Consistent — I feel hungry at regular times and stop when full"},
            {"label": "B", "value": "B", "text": "Slightly variable — some days more hungry than others"},
            {"label": "C", "value": "C", "text": "Unpredictable — my hunger fluctuates significantly"},
            {"label": "D", "value": "D", "text": "I rarely feel genuinely hungry — I eat by habit or schedule"},
            {"label": "E", "value": "E", "text": "I frequently overeat past the point of fullness"},
        ],
        "weight": 1.5,
    },
    {
        "section": "F",
        "number": 35,
        "text": "How do you feel in the 30 to 60 minutes after a typical meal?",
        "type": "select",
        "options": [
            {"label": "A", "value": "A", "text": "Light and energised — I feel good after eating"},
            {"label": "B", "value": "B", "text": "Neutral — neither energised nor heavy"},
            {"label": "C", "value": "C", "text": "A little heavy or sluggish but it passes"},
            {"label": "D", "value": "D", "text": "Heavy and tired — I often want to lie down or rest"},
            {"label": "E", "value": "E", "text": "Very heavy and uncomfortable — this happens almost every meal"},
        ],
        "weight": 1.5,
    },
]


async def seed_questions():
    """Create tables and seed all audit questions."""
    engine = create_async_engine(settings.database_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        for q_data in QUESTIONS:
            question = LifestyleAuditQuestion(
                id=str(uuid.uuid4()),
                section=q_data["section"],
                question_number=q_data["number"],
                question_text=q_data["text"],
                input_type=q_data["type"],
                options=q_data.get("options", []),
                weight=q_data.get("weight", 1.0),
            )
            session.add(question)

        await session.commit()
        print(f"✓ Seeded {len(QUESTIONS)} lifestyle audit questions")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_questions())

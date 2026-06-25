"""
Insert lifestyle audit questions directly into database.
"""
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.lifestyle_audit import Base, LifestyleAuditQuestion
from app.config import settings

QUESTIONS = [
    {"section": "B", "number": 7, "text": "What time do you usually go to sleep on weeknights?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Before 10 PM"}, {"label": "B", "value": "B", "text": "10 PM to 11 PM"}, {"label": "C", "value": "C", "text": "11 PM to midnight"}, {"label": "D", "value": "D", "text": "Midnight to 1 AM"}, {"label": "E", "value": "E", "text": "After 1 AM"}]},
    {"section": "B", "number": 8, "text": "What time do you usually wake up?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Before 6 AM"}, {"label": "B", "value": "B", "text": "6 AM to 7 AM"}, {"label": "C", "value": "C", "text": "7 AM to 8 AM"}, {"label": "D", "value": "D", "text": "After 8 AM"}, {"label": "E", "value": "E", "text": "I have no fixed wake time"}]},
    {"section": "B", "number": 9, "text": "On most nights, how many hours of actual sleep do you get?", "type": "select", "options": [{"label": "A", "value": "A", "text": "7 to 9 hours"}, {"label": "B", "value": "B", "text": "6 to 7 hours"}, {"label": "C", "value": "C", "text": "5 to 6 hours"}, {"label": "D", "value": "D", "text": "Less than 5 hours"}, {"label": "E", "value": "E", "text": "It varies a lot"}]},
    {"section": "B", "number": 10, "text": "When you wake up, how do you feel?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Rested and ready"}, {"label": "B", "value": "B", "text": "Groggy for 10-15 minutes"}, {"label": "C", "value": "C", "text": "Tired - want to sleep more"}, {"label": "D", "value": "D", "text": "Heavy and exhausted"}, {"label": "E", "value": "E", "text": "Never feel rested"}]},
    {"section": "B", "number": 11, "text": "What do you usually do in the last 30 minutes before sleeping?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Avoid screens"}, {"label": "B", "value": "B", "text": "Use phone occasionally"}, {"label": "C", "value": "C", "text": "Scroll social media"}, {"label": "D", "value": "D", "text": "Screen until sleep"}, {"label": "E", "value": "E", "text": "Fall asleep watching"}]},
    {"section": "B", "number": 12, "text": "How often do you have difficulty falling asleep?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Never"}, {"label": "B", "value": "B", "text": "Rarely"}, {"label": "C", "value": "C", "text": "Sometimes"}, {"label": "D", "value": "D", "text": "Often"}, {"label": "E", "value": "E", "text": "Almost every night"}]},
    {"section": "C", "number": 13, "text": "How many proper meals do you eat on a typical weekday?", "type": "select", "options": [{"label": "A", "value": "A", "text": "3+ meals"}, {"label": "B", "value": "B", "text": "2 meals, consistent"}, {"label": "C", "value": "C", "text": "2 meals, variable"}, {"label": "D", "value": "D", "text": "1 meal"}, {"label": "E", "value": "E", "text": "No pattern"}]},
    {"section": "C", "number": 14, "text": "Are your meal timings regular or irregular?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Very regular"}, {"label": "B", "value": "B", "text": "Usually regular"}, {"label": "C", "value": "C", "text": "Irregular"}, {"label": "D", "value": "D", "text": "Very irregular"}]},
    {"section": "C", "number": 15, "text": "What time do you usually finish dinner?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Before 7:30 PM"}, {"label": "B", "value": "B", "text": "7:30-8:30 PM"}, {"label": "C", "value": "C", "text": "8:30-9:30 PM"}, {"label": "D", "value": "D", "text": "After 9:30 PM"}, {"label": "E", "value": "E", "text": "After 10:30 PM"}]},
    {"section": "C", "number": 16, "text": "How often do you eat junk or processed food?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Rarely"}, {"label": "B", "value": "B", "text": "1-2 times/week"}, {"label": "C", "value": "C", "text": "3-4 times/week"}, {"label": "D", "value": "D", "text": "Most days"}, {"label": "E", "value": "E", "text": "Almost every meal"}]},
    {"section": "C", "number": 17, "text": "How often do you eat after 9 PM?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Rarely"}, {"label": "B", "value": "B", "text": "1-2 nights/week"}, {"label": "C", "value": "C", "text": "3-4 nights/week"}, {"label": "D", "value": "D", "text": "Most nights"}, {"label": "E", "value": "E", "text": "Every night"}]},
    {"section": "C", "number": 18, "text": "How would you describe your sugar cravings?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Low"}, {"label": "B", "value": "B", "text": "Moderate, managed"}, {"label": "C", "value": "C", "text": "High, give in"}, {"label": "D", "value": "D", "text": "Very high, daily"}]},
    {"section": "C", "number": 19, "text": "Do you eat differently when stressed?", "type": "select", "options": [{"label": "A", "value": "A", "text": "No"}, {"label": "B", "value": "B", "text": "Sometimes"}, {"label": "C", "value": "C", "text": "Often"}, {"label": "D", "value": "D", "text": "Yes, primary coping"}]},
    {"section": "C", "number": 20, "text": "How much water do you drink daily?", "type": "select", "options": [{"label": "A", "value": "A", "text": "2+ litres"}, {"label": "B", "value": "B", "text": "1-2 litres"}, {"label": "C", "value": "C", "text": "<1 litre"}, {"label": "D", "value": "D", "text": "Not tracked"}]},
    {"section": "D", "number": 21, "text": "How many days per week do you do intentional physical activity?", "type": "select", "options": [{"label": "A", "value": "A", "text": "5+ days"}, {"label": "B", "value": "B", "text": "3-4 days"}, {"label": "C", "value": "C", "text": "1-2 days"}, {"label": "D", "value": "D", "text": "<once/week"}, {"label": "E", "value": "E", "text": "None"}]},
    {"section": "D", "number": 22, "text": "On a typical day, how much do you walk?", "type": "select", "options": [{"label": "A", "value": "A", "text": "30+ minutes"}, {"label": "B", "value": "B", "text": "15-30 minutes"}, {"label": "C", "value": "C", "text": "<15 minutes"}, {"label": "D", "value": "D", "text": "Minimal"}]},
    {"section": "D", "number": 23, "text": "How long do you sit continuously without getting up?", "type": "select", "options": [{"label": "A", "value": "A", "text": "<1 hour"}, {"label": "B", "value": "B", "text": "1-2 hours"}, {"label": "C", "value": "C", "text": "2-3 hours"}, {"label": "D", "value": "D", "text": "3-4 hours"}, {"label": "E", "value": "E", "text": "4+ hours"}]},
    {"section": "D", "number": 24, "text": "Do you experience body pain or stiffness?", "type": "select", "options": [{"label": "A", "value": "A", "text": "No"}, {"label": "B", "value": "B", "text": "Minor stiffness"}, {"label": "C", "value": "C", "text": "Regular back/neck pain"}, {"label": "D", "value": "D", "text": "Daily pain"}]},
    {"section": "D", "number": 25, "text": "How would you describe your energy levels?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Consistently good"}, {"label": "B", "value": "B", "text": "Morning high, afternoon dip"}, {"label": "C", "value": "C", "text": "Afternoon crash"}, {"label": "D", "value": "D", "text": "Low most of day"}, {"label": "E", "value": "E", "text": "Exhausted"}]},
    {"section": "E", "number": 26, "text": "Rate your current stress level (1-10)", "type": "scale", "options": []},
    {"section": "E", "number": 27, "text": "What is your biggest source of stress?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Work"}, {"label": "B", "value": "B", "text": "Family/relationships"}, {"label": "C", "value": "C", "text": "Financial"}, {"label": "D", "value": "D", "text": "Health"}, {"label": "E", "value": "E", "text": "Multiple areas"}, {"label": "F", "value": "F", "text": "Not stressed"}]},
    {"section": "E", "number": 28, "text": "How often do your moods fluctuate?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Rarely"}, {"label": "B", "value": "B", "text": "Occasionally"}, {"label": "C", "value": "C", "text": "Often"}, {"label": "D", "value": "D", "text": "Very often"}]},
    {"section": "E", "number": 29, "text": "What is your primary motivation for joining?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Health concern"}, {"label": "B", "value": "B", "text": "Lose weight"}, {"label": "C", "value": "C", "text": "More energy"}, {"label": "D", "value": "D", "text": "Build habits"}, {"label": "E", "value": "E", "text": "Recommendation"}]},
    {"section": "E", "number": 30, "text": "Biggest challenge in maintaining healthy habits?", "type": "select", "options": [{"label": "A", "value": "A", "text": "No time"}, {"label": "B", "value": "B", "text": "Cannot stay consistent"}, {"label": "C", "value": "C", "text": "No support"}, {"label": "D", "value": "D", "text": "Food access"}, {"label": "E", "value": "E", "text": "Stress"}, {"label": "F", "value": "F", "text": "Never tried"}]},
    {"section": "F", "number": 31, "text": "How often do you experience bloating?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Rarely"}, {"label": "B", "value": "B", "text": "1-2x/week"}, {"label": "C", "value": "C", "text": "Several/week"}, {"label": "D", "value": "D", "text": "Most days"}, {"label": "E", "value": "E", "text": "Every meal"}]},
    {"section": "F", "number": 32, "text": "How would you describe your bowel pattern?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Regular"}, {"label": "B", "value": "B", "text": "Mostly regular"}, {"label": "C", "value": "C", "text": "Every 2+ days"}, {"label": "D", "value": "D", "text": "Irregular"}, {"label": "E", "value": "E", "text": "Constipation"}]},
    {"section": "F", "number": 33, "text": "How often do you experience acidity/heartburn?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Never"}, {"label": "B", "value": "B", "text": "1-2x/month"}, {"label": "C", "value": "C", "text": "1-2x/week"}, {"label": "D", "value": "D", "text": "Most days"}, {"label": "E", "value": "E", "text": "Multiple daily"}]},
    {"section": "F", "number": 34, "text": "How would you describe your appetite?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Consistent"}, {"label": "B", "value": "B", "text": "Slightly variable"}, {"label": "C", "value": "C", "text": "Unpredictable"}, {"label": "D", "value": "D", "text": "Rarely hungry"}, {"label": "E", "value": "E", "text": "Overeat often"}]},
    {"section": "F", "number": 35, "text": "How do you feel 30-60 min after meals?", "type": "select", "options": [{"label": "A", "value": "A", "text": "Light, energised"}, {"label": "B", "value": "B", "text": "Neutral"}, {"label": "C", "value": "C", "text": "Slightly heavy"}, {"label": "D", "value": "D", "text": "Heavy, tired"}, {"label": "E", "value": "E", "text": "Very heavy"}]},
]

# Get sync database URL (convert postgresql+asyncpg to postgresql)
db_url = settings.database_url.replace('postgresql+asyncpg://', 'postgresql://')

engine = create_engine(db_url, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Clear existing questions
    session.query(LifestyleAuditQuestion).delete()

    # Add all questions
    for q_data in QUESTIONS:
        question = LifestyleAuditQuestion(
            id=str(uuid.uuid4()),
            section=q_data["section"],
            question_number=q_data["number"],
            question_text=q_data["text"],
            input_type=q_data["type"],
            options=q_data.get("options", []),
            weight=1.0,
        )
        session.add(question)

    session.commit()
    print(f"[OK] Successfully seeded {len(QUESTIONS)} lifestyle audit questions!")
except Exception as e:
    session.rollback()
    print(f"[ERROR] {e}")
finally:
    session.close()

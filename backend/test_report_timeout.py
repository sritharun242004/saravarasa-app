import asyncio
import httpx
import json
from datetime import datetime

async def test_report_with_timeout():
    base_url = 'http://localhost:8001'

    # 1. Create test user
    user_data = {
        'name': 'Test User',
        'phone': '9876543210',
        'email': 'testuser@example.com',
        'password': 'Test123!@#'
    }
    async with httpx.AsyncClient() as client:
        # Signup
        resp = await client.post(f'{base_url}/auth/signup', json=user_data)
        if resp.status_code != 200:
            print(f'Signup failed: {resp.text}')
            return

        data = resp.json()
        client_id = data.get('client_id')
        token = data.get('token')
        print(f'✓ User created: {client_id}')

        # 2. Complete profile
        profile_data = {
            'name': 'Test User',
            'phone': '9876543210',
            'email': 'test@example.com',
            'sex': 'Male',
            'gender': 'Male',
            'age': 30,
            'height_cm': 175,
            'weight_kg': 75
        }
        resp = await client.patch(
            f'{base_url}/profile/{client_id}',
            json=profile_data,
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f'✓ Profile completed: {resp.status_code}')

        # 3. Log meals for 7 days (minimal logging to reach compliance)
        for day in range(1, 8):
            for meal in ['breakfast', 'lunch', 'dinner']:
                log_data = {
                    'day_number': day,
                    'meal_type': meal,
                    'meal_text': f'Wholesome {meal} - Day {day}',
                    'food_pattern_tags': ['PROTEIN_PRESENT', 'VEGETABLE_PRESENT'],
                    'image_url': f'https://example.com/meal{day}.jpg'
                }
                resp = await client.post(
                    f'{base_url}/meals/log',
                    json=log_data,
                    headers={'Authorization': f'Bearer {token}'}
                )
                if resp.status_code == 200:
                    print(f'  ✓ Logged {meal} Day {day}')

        # 4. Trigger report generation
        print('\n⏱️ Triggering report generation with 30s timeout...')
        print('   (LLM will timeout and fallback to rule-based report)\n')

        resp = await client.get(
            f'{base_url}/reports/{client_id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        if resp.status_code == 200:
            report = resp.json()
            print(f'✓ Report generated successfully!')
            print(f'  Compliance: {report.get("compliance_score", "N/A")}%')
            print(f'  Commitment Level: {report.get("commitment_level", "N/A")}')
            print(f'  Recommendations: {len(report.get("food_recommendations", []))} items')
            print(f'  Has summary: {bool(report.get("llm_summary", ""))}')
        else:
            print(f'Report generation failed: {resp.text}')

asyncio.run(test_report_with_timeout())

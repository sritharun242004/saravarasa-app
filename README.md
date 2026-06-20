# NutriLens Challenge Platform

A **cohort-based 7-day weight loss qualification platform** for Indian cuisine. Clients join a batch, submit daily meals as plain text, and are scored for compliance, meal quality, and consistency — producing an eligibility score that coaches use to enrol the right people into paid weight loss programs.

> **Phase 1 focus:** Behaviour change + qualification, not AI vision. The INDB nutrition engine is kept as a text-based analysis service. Gemini Vision, embeddings, and the knowledge graph are removed.

---

## How It Works

```
Client Onboards
      ↓
Joins a 7-Day Batch (e.g. "July Batch")
      ↓
Submits 3 Meals / Day as Plain Text
      ↓
Compliance Engine tracks 21 required meals
      ↓
Meal Pattern Engine analyses 7-day nutrition
      ↓
Eligibility Engine scores: Compliance + Quality + Consistency + Engagement
      ↓
Coach Reviews → Enrolls in Paid Program
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy async, asyncpg |
| **Database** | PostgreSQL 16 (Neon cloud or local) |
| **Nutrition Data** | INDB 2024.11 — 1,014 Indian foods, 39 nutrients tracked |

**Removed in Phase 1:** Gemini Vision API · pgvector · Embeddings · Semantic search · Knowledge graph · Question engine

---

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- PostgreSQL 16 (or Neon cloud — `DATABASE_URL` in `backend/.env`)

### Run Locally (Verified)

**Backend** — open a terminal in `backend/`:
```bash
# First time only
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt

# Every time
venv\Scripts\activate
uvicorn app.main:app --reload --port 8001
```

Backend runs at: http://localhost:8001  
Interactive API docs: http://localhost:8001/docs

**Frontend** — open a separate terminal in `frontend/`:
```bash
# First time only
npm install

# Every time
npm run dev
```

Frontend runs at: http://localhost:3000

### Run with Docker

```bash
cd nutrilens-india
cp .env.example .env   # add your DATABASE_URL
docker-compose up -d
```

---

## Environment Variables

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/nutrilens
INDB_FILE_PATH=./data/Anuvaad_INDB_2024.11.xlsx
UPLOAD_DIR=./uploads
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=change-in-production
```

---

## Database Schema

### `clients`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name, age, gender | | |
| height_cm, weight_kg | float | |
| goal | text | e.g. "Lose 5kg in 3 months" |
| phone, email | | |
| batch_id | FK → challenge_batches | |
| joined_at | timestamp | |
| status | enum | `ACTIVE · PASSED · FAILED · ENROLLED` |

### `challenge_batches`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | text | e.g. "July Batch" |
| start_date, end_date | date | |
| capacity | int | default 100 |

### `meal_logs`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| client_id | FK | |
| day_number | int | 1–7 |
| meal_type | enum | `BREAKFAST · LUNCH · DINNER` |
| meal_text | text | Free text e.g. "3 idli, sambar, tea" |
| submitted_at | timestamp | |

### `compliance_scores`
| Column | Type | Notes |
|--------|------|-------|
| client_id | FK PK | |
| required_meals | int | 21 (7 days × 3 meals) |
| submitted_meals | int | |
| compliance_pct | float | |
| status | enum | `PASSING · FAILED · COMPLETE` |

### `nutrition_summary`
| Column | Type | Notes |
|--------|------|-------|
| client_id | FK PK | |
| total_calories, total_protein, total_carbs, total_fat, total_fiber | float | 7-day totals |
| protein_pct, carb_pct, fat_pct | float | % of total calories |
| meal_pattern | text | e.g. `CARB_HEAVY` |

### `challenge_reports`
| Column | Type | Notes |
|--------|------|-------|
| client_id | FK PK | |
| compliance_score | float | 0–100 |
| eligibility_score | float | 0–100 |
| eligibility_band | text | `GOLD · STRONG · MODERATE · NOT_READY` |
| meal_pattern | text | |
| strengths | text[] | |
| improvement_areas | text[] | |
| action_plan | text[] | |
| generated_at | timestamp | |
| report_url | text | PDF / shareable link |

---

## API Endpoints

### Onboarding
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/onboarding/register` | Create client + assign to batch |
| `GET` | `/onboarding/batches` | List open batches |

### Challenge (Client)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/challenge/submit-meal` | Submit one meal (day, type, text) |
| `GET` | `/challenge/progress/{client_id}` | Days remaining, meals submitted, current status |
| `GET` | `/challenge/day/{client_id}/{day}` | Meals submitted for a specific day |

### Compliance
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/compliance/{client_id}` | Compliance %, submitted vs required |
| `GET` | `/compliance/batch/{batch_id}` | Full batch compliance summary |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reports/generate/{client_id}` | Generate eligibility report (requires ≥ 85% compliance) |
| `GET` | `/reports/{client_id}` | Retrieve generated report |

### Admin / Coach Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/clients` | All clients with status + eligibility scores |
| `GET` | `/admin/clients/{id}` | Single client detail view |
| `GET` | `/admin/batch/{batch_id}/summary` | Batch stats: passed / failed / gold candidates |

### Foods (Nutrition Engine)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/foods/autocomplete` | Food name search (`?q=`) |
| `GET` | `/foods/nutrition` | Unit-serving nutrition for a food (`?name=`) |

---

## Project Structure

```
nutrilens-india/
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   # Landing / challenge intro
│   │   ├── register/page.tsx          # Client onboarding form
│   │   ├── dashboard/page.tsx         # Client: 7-day progress
│   │   ├── challenge/
│   │   │   └── [day]/page.tsx         # Daily meal submission (3 text areas)
│   │   ├── report/[clientId]/page.tsx # Final eligibility report
│   │   └── admin/
│   │       ├── page.tsx               # Coach: batch overview
│   │       └── [clientId]/page.tsx    # Coach: client detail
│   ├── components/
│   │   ├── challenge/
│   │   │   ├── progress-bar.tsx       # Meals submitted / compliance %
│   │   │   ├── meal-form.tsx          # 3-textarea daily submission
│   │   │   └── status-badge.tsx       # PASSING / FAILED badge
│   │   ├── report/
│   │   │   ├── eligibility-card.tsx   # Score + band (Gold / Strong / …)
│   │   │   ├── nutrition-summary.tsx  # 7-day macro breakdown
│   │   │   └── action-plan.tsx        # Improvement areas + recommendations
│   │   ├── admin/
│   │   │   ├── client-table.tsx       # Sortable client list
│   │   │   └── batch-stats.tsx        # Passed / Failed / Gold counts
│   │   └── ui/                        # shadcn/ui primitives
│   └── lib/api.ts                     # API client + TypeScript interfaces
│
├── backend/
│   └── app/
│       ├── routes/
│       │   ├── onboarding.py          # Register client, list batches
│       │   ├── challenge.py           # Submit meals, get progress
│       │   ├── compliance.py          # Compliance tracking
│       │   ├── reports.py             # Report generation
│       │   └── admin.py              # Coach dashboard endpoints
│       ├── services/
│       │   ├── meal_parser.py         # Parse free-text → food items
│       │   ├── food_matcher.py        # Match food names to INDB
│       │   ├── nutrition_engine.py    # 7-day nutrition aggregation
│       │   ├── compliance_engine.py   # Count meals, calc % + status
│       │   ├── pattern_engine.py      # Classify meal pattern
│       │   ├── eligibility_engine.py  # Weighted eligibility score
│       │   └── report_engine.py       # Assemble + render report
│       ├── models/
│       │   ├── client.py              # Client, ChallengeBatch ORM
│       │   ├── meal_log.py            # MealLog ORM
│       │   └── report.py             # ComplianceScore, NutritionSummary, ChallengeReport ORM
│       ├── config.py
│       ├── database.py
│       └── main.py
│
├── data/
│   └── Anuvaad_INDB_2024.11.xlsx     # INDB dataset (not committed to git)
│
├── NutriLens_India_Overview.html      # Customer pitch document
└── docker-compose.yml
```

---

## Eligibility Scoring

The eligibility score (0–100) is a weighted combination of four factors:

| Factor | Weight | How it's measured |
|--------|--------|-------------------|
| **Compliance** | 40% | Meals submitted ÷ 21 required |
| **Meal Quality** | 30% | Protein %, fibre, low processed foods |
| **Consistency** | 20% | No missed days; balanced across 7 days |
| **Engagement** | 10% | On-time submissions, variety |

**Eligibility bands:**

| Score | Band | Action |
|-------|------|--------|
| 90–100 | 🥇 Gold Candidate | Priority enrolment |
| 80–89 | Strong Candidate | Standard enrolment |
| 70–79 | Moderate | Re-challenge recommended |
| < 70 | Not Ready | Coaching notes provided |

---

## Meal Pattern Classification

The pattern engine aggregates 7 days of nutrition and assigns one label:

| Pattern | Criteria |
|---------|---------|
| `BALANCED` | Protein 20–30%, Carb 45–55%, Fat 20–30% |
| `CARB_HEAVY` | Carbs > 60% of calories |
| `PROTEIN_DEFICIENT` | Protein < 12% of calories |
| `HIGH_SUGAR` | Free sugars > 10% of calories |
| `LOW_FIBER` | Fibre < 15g/day average |
| `HIGH_CALORIE` | > 2,400 kcal/day average |
| `VEGETARIAN_BALANCED` | No meat + Balanced macros |

---

## INDB Nutrition Engine

The engine (`backend/app/services/nutrition_engine.py`) parses free-text meal submissions into INDB-matched food items:

1. **Text parsing** — splits "3 idli, sambar, tea" into quantity + food name tokens
2. **Food matching** — maps names to INDB entries with 30+ synonym expansions (`chai → tea`, `roti → chapati`)
3. **Portion estimation** — applies quantity multipliers to unit-serving values
4. **Aggregation** — sums across all meals in a day; across all 7 days for the challenge report

---

## Compliance Rules

- **Required meals:** 21 (7 days × 3 meals per day)
- **Status `PASSING`:** ≥ 85% submitted (≥ 18 meals) with no 2 consecutive missed days
- **Status `FAILED`:** < 85% submitted or 2+ consecutive missed days
- **Report generation** is locked until compliance ≥ 85%
Open two terminal windows (PowerShell or CMD) from c:\Users\mohanraj\Desktop\sarvarasa\nutrilens-india\:

Terminal 1 — Backend


cd c:\Users\mohanraj\Desktop\sarvarasa\nutrilens-india\backend
venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


Terminal 2 — Frontend

cd c:\Users\mohanraj\Desktop\sarvarasa\nutrilens-india\frontend
npm run dev


Then open your browser:

What	URL
App	http://localhost:3000
API docs	http://localhost:8000/docs
Food search test	http://localhost:8000/foods/search?q=idli
First time only — run the INDB food import (one time, populates the food database):


cd c:\Users\mohanraj\Desktop\sarvarasa\nutrilens-india\backend
venv\Scripts\python scripts\import_indb.py
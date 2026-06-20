# Import all models so SQLAlchemy's Base.metadata registers them for init_db()
from app.models.client import Client, ChallengeBatch                                 # noqa: F401
from app.models.meal_log import MealLog                                              # noqa: F401
from app.models.report import ComplianceScore, NutritionSummary, ChallengeReport    # noqa: F401
from app.models.audit import LifestyleAudit                                          # noqa: F401
from app.models.food_alias import FoodAlias                                          # noqa: F401  (food_keyword_aliases)
from app.models.food import Food                                                     # noqa: F401
from app.models.food_alias_search import FoodAliasSearch                             # noqa: F401  (food_aliases)
from app.models.meal_food import MealFood                                            # noqa: F401
from app.models.challenge_attempt import ChallengeAttempt                            # noqa: F401
from app.models.payment import PaymentTransaction                                    # noqa: F401

from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    content_safety_model: str = "nvidia/nemotron-3.5-content-safety:free"
    llm_report_model: str = "meta-llama/llama-3.3-70b-instruct:free"
    database_url: str = ""
    indb_file_path: str = "./data/Anuvaad_INDB_2024.11.xlsx"
    upload_dir: str = "./uploads"
    secret_key: str = "change-me-in-production"
    cors_origins: List[str] = ["http://localhost:3000"]
    max_upload_size_mb: int = 10
    razorpay_key_id: str = ""
    razorpay_key_secret: str = "dev_secret"

    # ─── Admin console credentials (sourced from env — never hardcode) ───────
    admin_email: str = ""
    admin_password: str = ""

    # ─── AWS Cognito + Google OAuth ──────────────────────────────────────────
    # All values come from the environment — never hardcode secrets here.
    cognito_region: str = "eu-north-1"
    cognito_user_pool_id: str = ""          # e.g. eu-north-1_bLTFnMCcW
    cognito_domain: str = ""                # e.g. https://<prefix>.auth.<region>.amazoncognito.com
    cognito_app_client_id: str = ""         # Cognito User Pool app-client ID (NOT the Google client id)
    cognito_app_client_secret: str = ""     # only if the app client was created with a secret
    google_client_id: str = ""              # Google OAuth client id federated into Cognito
    oauth_redirect_uri: str = "http://localhost:3000/auth/callback"  # app callback (allowed in Cognito)
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

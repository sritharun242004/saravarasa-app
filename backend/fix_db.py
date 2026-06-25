#!/usr/bin/env python3
"""Directly add missing columns to the database"""
import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def fix_database():
    """Add missing columns to clients table"""
    load_dotenv('.env')

    async with AsyncSessionLocal() as session:
        try:
            # Add sex column if it doesn't exist
            await session.execute(text("""
                ALTER TABLE clients
                ADD COLUMN IF NOT EXISTS sex VARCHAR
            """))
            print("[OK] Added sex column")

            # Add profile_completed column if it doesn't exist
            await session.execute(text("""
                ALTER TABLE clients
                ADD COLUMN IF NOT EXISTS profile_completed BOOLEAN DEFAULT false
            """))
            print("[OK] Added profile_completed column")

            # Add profile_updated_at column if it doesn't exist
            await session.execute(text("""
                ALTER TABLE clients
                ADD COLUMN IF NOT EXISTS profile_updated_at TIMESTAMP WITH TIME ZONE
            """))
            print("[OK] Added profile_updated_at column")

            # Create test_attempts table if it doesn't exist
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS test_attempts (
                    id VARCHAR PRIMARY KEY,
                    client_id VARCHAR NOT NULL,
                    test_type VARCHAR NOT NULL,
                    challenge_cycle INTEGER,
                    score FLOAT,
                    status VARCHAR,
                    answers JSON,
                    submitted_at TIMESTAMP WITH TIME ZONE,
                    unlocked_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE,
                    FOREIGN KEY (client_id) REFERENCES clients(id)
                )
            """))
            print("[OK] Created test_attempts table")

            # Create questions table if it doesn't exist
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS questions (
                    id VARCHAR PRIMARY KEY,
                    test_type VARCHAR NOT NULL,
                    question_text TEXT NOT NULL,
                    "order" INTEGER,
                    options JSON,
                    correct_answer VARCHAR,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE,
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("[OK] Created questions table")

            await session.commit()
            print("\nDatabase schema updated successfully!")
            return True
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()
            return False

if __name__ == "__main__":
    result = asyncio.run(fix_database())
    exit(0 if result else 1)

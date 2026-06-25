#!/usr/bin/env python3
"""Run Alembic migration with .env loaded"""
import os
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command

# Load .env
load_dotenv('.env')

# Run migration
config = Config("alembic.ini")
command.upgrade(config, "head")
print("Migration completed successfully!")

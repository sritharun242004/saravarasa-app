"""Shared slowapi Limiter — in-memory, keyed by client IP.

In-memory storage means limits are per-process (fine for a single backend
instance; switch the storage_uri to Redis if this is ever scaled out).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

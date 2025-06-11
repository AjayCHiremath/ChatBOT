# utils/env.py
import os
from dotenv import load_dotenv

def load_environment(keys):
    load_dotenv()
    for key in keys:
        value = os.getenv(key)
        if value:
            os.environ[key] = value
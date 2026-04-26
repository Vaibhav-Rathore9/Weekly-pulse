"""Allow running Phase 3 as a module: python -m src.phase3"""
from dotenv import load_dotenv
load_dotenv()

from .cli import run

if __name__ == "__main__":
    run()

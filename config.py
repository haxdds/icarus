import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alpaca credentials pulled from environment variables:
API_KEYS = {
    'H1': {'key': os.getenv("H1_API_KEY"), 'secret': os.getenv("H1_API_SECRET")},
    'H2': {'key': os.getenv("H2_API_KEY"), 'secret': os.getenv("H2_API_SECRET")},
    'H3': {'key': os.getenv("H3_API_KEY"), 'secret': os.getenv("H3_API_SECRET")},
    'R1': {'key': os.getenv("R1_API_KEY"), 'secret': os.getenv("R1_API_SECRET")},
    'R2': {'key': os.getenv("R2_API_KEY"), 'secret': os.getenv("R2_API_SECRET")},
    'R3': {'key': os.getenv("R3_API_KEY"), 'secret': os.getenv("R3_API_SECRET")}
}

BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading URL
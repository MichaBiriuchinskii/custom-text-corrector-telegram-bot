import os
from dotenv import load_dotenv

load_dotenv()

LOG_FILE_PATH = os.path.expanduser("~/custom-text-corrector-telegram-bot/telegram_custom_corrector.log")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODEL_NAME = "meta-llama/llama-4-maverick:free"

API_BASE_URL = "https://openrouter.ai/api/v1"

X_TITLE = "Custom Text Corrector"
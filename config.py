import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODEL_NAME = "meta-llama/llama-4-maverick:free"


HTTP_REFERER = "https://your-telegram-bot-project.com"
X_TITLE = "Custom Text Corrector"
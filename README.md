# Custom Text Corrector Telegram Bot

A personal Telegram bot that provides tailored grammar and style corrections using free LLM APIs from OpenRouter. This bot solves the frustration of using ChatGPT or other tools where you have to explain prompts and ask specifically not to fix too much while still getting meaningful corrections.

## 🎯 Why This Bot?

Traditional correction tools often over-correct or don't understand your specific needs. This solution gives you:
- Tailored corrections based on your preferences
- Multiple correction modes (full, grammar-only, style-only)
- Custom tone adjustments
- Multi-language support
- No need to explain prompts each time

## ✨ Features

- **Smart Grammar Correction**: Fix grammar and spelling while preserving your style
- **Tone Adjustment**: Choose from preset tones (casual, formal, polite, academic) or create custom ones
- **Multiple Correction Modes**:
  - Full correction (grammar + style)
  - Grammar-only (preserves original tone)
  - Style-only (adjusts tone without fixing grammar)
- **Multi-language Support**: Auto-detects and responds in the same language
- **Rate Limiting**: Prevents spam and API abuse
- **Interactive Interface**: Easy-to-use inline keyboards
- **Persistent Settings**: Remembers your preferences

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Telegram Bot Token (from @BotFather)
- OpenRouter API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd custom-text-corrector-telegram-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   
   Create a `.env` file in the root directory:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL_NAME=meta-llama/llama-3.1-8b-instruct:free
   API_BASE_URL=https://openrouter.ai/api/v1
   HTTP_REFERER=your_app_name
   X_TITLE=your_app_name
   LOG_FILE_PATH=telegram_custom_corrector.log
   ```

   Create a `config.py` file to load these variables:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
   OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
   OPENROUTER_MODEL_NAME = os.getenv('OPENROUTER_MODEL_NAME')
   API_BASE_URL = os.getenv('API_BASE_URL')
   HTTP_REFERER = os.getenv('HTTP_REFERER')
   X_TITLE = os.getenv('X_TITLE')
   LOG_FILE_PATH = os.getenv('LOG_FILE_PATH')
   ```

### Running the Bot

**For development:**
```bash
python bot.py
```

**For production (background process):**
```bash
nohup python bot.py > /dev/null 2>&1 &
```

### Managing the Background Process

**Find the running process:**
```bash
ps aux | grep bot.py
```

**Kill the process:**
```bash
kill PID  # Replace PID with the actual process ID
```

**Monitor logs:**
```bash
tail -f telegram_custom_corrector.log
```

## 🔧 Configuration

### OpenRouter Setup

1. Sign up at [OpenRouter](https://openrouter.ai)
2. Get your free API key
3. Choose a free model (e.g., `meta-llama/llama-3.1-8b-instruct:free`)

### Telegram Bot Setup

1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token
4. Add the token to your `.env` file

## 📱 Usage

### Basic Commands

- `/start` - Show welcome message and features
- `/help` - Display help information
- `/tone` - Choose correction tone
- `/mode` - Select correction mode
- `/settings` - View current preferences

### Correction Modes

1. **Full Correction** (default)
   - Fixes grammar and spelling
   - Adjusts tone and style
   - Most comprehensive option

2. **Grammar Only**
   - Only fixes grammar and spelling errors
   - Preserves original tone and style
   - Perfect for maintaining your voice

3. **Style Only**
   - Adjusts tone without fixing grammar
   - Useful for changing formality level
   - Keeps original errors intact

### Tone Presets

- **Casual**: Conversational and relaxed
- **Formal**: Business-like and professional
- **Polite**: Respectful and courteous
- **Academic**: Scholarly and intellectual
- **Custom**: Define your own tone

### Example Usage

Simply send any message to the bot:

**Input:** "Эмм я честно не знаю что ты хотел в претпоследгнем сообщении сказать"
**Output:** "Эм, я, если честно, не знаю, что ты хотел в предпоследнем сообщении сказать"

**Input:** "I has a apple"
**Output:** "I have an apple"

## 🛠️ Technical Details

### Architecture

- **Framework**: python-telegram-bot
- **LLM Integration**: LangChain with OpenAI-compatible API
- **Rate Limiting**: Custom decorator to prevent abuse
- **Logging**: Comprehensive logging to file and console
- **Error Handling**: Graceful error recovery

### Rate Limiting

- 10 messages per minute per user
- Prevents API abuse and ensures fair usage

### Logging

All activity is logged to `telegram_custom_corrector.log` including:
- User interactions
- LLM requests and responses
- Errors and exceptions
- Bot startup and shutdown

### File Structure

```
custom-text-corrector-telegram-bot/
├── bot.py                 # Main bot application
├── config.py             # Configuration loader
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── telegram_custom_corrector.log  # Log file
└── README.md            # This file
```

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if the process is running: `ps aux | grep bot.py`
   - Check logs: `tail -f telegram_custom_corrector.log`
   - Verify API keys in `.env` file

2. **API errors**
   - Verify OpenRouter API key
   - Check if model name is correct
   - Ensure you have API credits

3. **Permission errors**
   - Make sure the bot has write permissions for log files
   - Check if virtual environment is activated

### Log Analysis

Check the log file for detailed error information:
```bash
tail -n 100 telegram_custom_corrector.log
```

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is for personal use. Please respect OpenRouter's terms of service and Telegram's bot guidelines.

---

## 👨‍💻 Author

**Mikhail Biriuchinskii** - R&D Data Scientist & NLP Specialist in Paris

Expertise in text processing, LLMs, multilingual systems, and building tools at the intersection of language, AI, and data. This bot leverages prompt engineering and LLM fine-tuning principles to deliver tailored text corrections.

🔗 [GitHub Profile](https://github.com/MichaBiriuchinskii)

---

Made with ❤️ for better text communication
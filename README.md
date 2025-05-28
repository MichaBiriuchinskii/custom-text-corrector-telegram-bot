# Custom Text Corrector Telegram Bot

Tired of opening ChatGPT, Gemini, or other LLM apps just to fix a sentence? This personal Telegram bot makes tailored grammar and style corrections just a message away — directly from your favorite messaging app.


## Why This Bot?

Most tools rewrite too much or miss your tone. This bot gives fast, personal corrections — right in Telegram.

- 🧠 Remembers your style and preferences
- 🎛️ Choose: full, grammar-only, or style-only
- 🎯 Set your tone once — formal, casual, etc.
- 🌍 Works in multiple languages
- 🚫 No need to explain prompts each time


## Features

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
- Errors and exceptions
- Bot startup and shutdown

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

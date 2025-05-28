import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Import configuration
import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- LLM Interaction ---
llm = None

def initialize_llm():
    global llm
    try:
        llm = ChatOpenAI(
            temperature=0.5, # Adjust for creativity vs. strictness
            model_name=config.OPENROUTER_MODEL_NAME,
            openai_api_key=config.OPENROUTER_API_KEY,
            max_tokens=500,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": config.HTTP_REFERER,
                "X-Title": config.X_TITLE,
            }
        )
        logger.info(f"LLM initialized with model: {config.OPENROUTER_MODEL_NAME}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        llm = None

def get_corrected_text(user_text: str, desired_tone: str = "neutral and professional") -> str | None:
    if not llm:
        logger.error("LLM not initialized. Cannot process request.")
        return "Sorry, the correction service is currently unavailable."

    # This is where you craft your prompt!
    # It's crucial for getting good results.
    system_prompt_content = f"""You are an expert language assistant.
Your task is to meticulously correct the grammar and spelling errors in the user's message.
Additionally, refine the style for clarity and conciseness.
Adjust the tone of the message to be {desired_tone}.
Output ONLY the corrected message, without any preambles, explanations, or conversational filler.
If the message is already perfect, return it as is.
Do not add any quotation marks around your response unless they were part of the original message and should be preserved.
Never include dashes or bullet points in your response.
Define automaticly the language of the message based on its content.
"""

    messages = [
        SystemMessage(content=system_prompt_content),
        HumanMessage(content=user_text),
    ]

    try:
        logger.info(f"Sending to LLM. System prompt: {system_prompt_content[:100]}... User text: {user_text[:100]}...")
        response = llm.invoke(messages)
        corrected_text = response.content.strip() if hasattr(response, 'content') else str(response).strip()
        logger.info(f"LLM response: {corrected_text[:100]}...")
        return corrected_text
    except Exception as e:
        logger.error(f"Error during LLM invocation: {e}")
        return "Sorry, I encountered an error while trying to correct your message."

# --- Telegram Bot Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text(
        "Hello! I'm your grammar, style, and tone correction bot.\n\n"
        "Just send me any message, and I'll try my best to correct it for you.\n\n"
        "You can also specify a desired tone using /tone [your desired tone] before sending your message. "
        "For example: `/tone friendly and casual` then send your message in the next chat."
        "If no tone is specified, I'll aim for a 'neutral and professional' tone."
    )

async def tone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets the desired tone for corrections."""
    try:
        desired_tone = " ".join(context.args)
        if not desired_tone:
            await update.message.reply_text("Please specify a tone. Example: /tone polite and formal")
            return
        context.user_data['desired_tone'] = desired_tone
        await update.message.reply_text(f"Tone set to: '{desired_tone}'. I'll use this for your next messages.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /tone <your desired tone>")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles regular messages and corrects them."""
    user_message_text = update.message.text
    chat_id = update.message.chat_id

    if not user_message_text:
        return

    logger.info(f"Received message from {chat_id}: {user_message_text[:100]}...")

    # Get desired tone from user_data or use default
    desired_tone = context.user_data.get('desired_tone', "neutral and professional")
    logger.info(f"Using tone: '{desired_tone}' for correction.")

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    corrected_message = get_corrected_text(user_message_text, desired_tone)

    if corrected_message:
        await update.message.reply_text(corrected_message)
    else:
        await update.message.reply_text("Sorry, I couldn't process your message.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    # Initialize LLM on startup
    initialize_llm()
    if not llm:
        logger.error("LLM could not be initialized. Bot cannot start.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("tone", tone_command))

    # on non command i.e message - correct the message
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # log all errors
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    logger.info("Starting bot polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
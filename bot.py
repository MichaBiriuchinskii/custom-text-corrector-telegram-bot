import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import config
import asyncio
from functools import wraps

# Enable logging
logging.basicConfig(
    filename=config.LOG_FILE_PATH, 
    filemode='a',
    encoding='utf-8',
    datefmt='%Y-%m-%d %H:%M:%S',
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)
logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {config.LOG_FILE_PATH}")

# --- Constants ---
TONE_PRESETS = {
    "casual": "casual and conversational",
    "formal": "formal and business-like",
    "polite": "polite and respectful",
    "academic": "academic and scholarly, higly intellectual and even pedantic",

}

# Rate limiting decorator
def rate_limit(max_calls=5, time_window=60):
    def decorator(func):
        calls = {}
        
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            current_time = asyncio.get_event_loop().time()
            
            if user_id not in calls:
                calls[user_id] = []
            
            # Remove old calls outside time window
            calls[user_id] = [call_time for call_time in calls[user_id] 
                             if current_time - call_time < time_window]
            
            if len(calls[user_id]) >= max_calls:
                await update.message.reply_text(
                    f"⏰ Rate limit exceeded. Please wait a moment before sending another message."
                )
                return
            
            calls[user_id].append(current_time)
            return await func(update, context)
        
        return wrapper
    return decorator

# --- LLM Interaction ---
llm = None

def initialize_llm():
    global llm
    try:
        llm = ChatOpenAI(
            temperature=0.7,
            model_name=config.OPENROUTER_MODEL_NAME,
            openai_api_key=config.OPENROUTER_API_KEY,
            max_tokens=500,  
            openai_api_base=config.API_BASE_URL,
            default_headers={
                "HTTP-Referer": config.HTTP_REFERER,
                "X-Title": config.X_TITLE,
            }
        )
        logger.info(f"LLM initialized with model: {config.OPENROUTER_MODEL_NAME}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        llm = None

def get_corrected_text(user_text: str, desired_tone: str = "neutral and professional", correction_mode: str = "full") -> str | None:
    if not llm:
        logger.error("LLM not initialized. Cannot process request.")
        return "Sorry, the correction service is currently unavailable."

    if correction_mode == "grammar_only":
        system_prompt_content = f"""
You are a grammar and spelling correction assistant. 

STRICT RULES:
- ONLY fix grammar mistakes, spelling errors, and punctuation issues
- Do NOT change tone, style, vocabulary, or sentence structure
- Keep all original word choices and expressions
- If there are no actual errors, return the exact same text
- Preserve the user's natural speaking style completely
- Do not add a full stop at the end of the text, if it doesn't already have one and the tone is not professional

Return only the corrected text without quotation marks or explanations.
"""
    elif correction_mode == "style_only":
        system_prompt_content = f"""
You are a style and tone adjustment assistant.

STRICT RULES:
- Change ONLY the tone and style to be: {desired_tone}
- Do NOT fix grammar or spelling errors - leave them as they are
- Focus on adjusting formality level, word choices, and expressions
- Keep the same meaning but adjust how it sounds
- If the tone is already appropriate, make no changes
- Do not add a full stop at the end of the text, if it doesn't already have one and the tone is not professional

Return only the style-adjusted text without quotation marks or explanations.
"""
    else:
        system_prompt_content = f"""
You are a comprehensive text correction assistant.

Instructions:
- Fix grammar and spelling errors
- Adjust the tone to be: {desired_tone}
- Make sure the corrected text sounds natural
- Auto-detect the language and respond in the same language
- Do not add a full stop at the end of the text, if it doesn't already have one and the tone is not professional
- If the message needs no changes, return it unchanged

Return only the corrected text without quotation marks, dashes, full stop ath the end, explanations, or formatting.

Examples: 
- "Эмм я честно не знаю что ты хотел в претпоследгнем сообщении сказать" (tone: casual) -> "Эм, я, если честно, не знаю, что ты хотел в предпоследнем сообщении сказать"
- "I has a apple" (tone: neutral) -> "I have an apple."
- "adding new functionalities" (tone: casual) -> "adding new functionalities"
- "Can you help me with this?" (tone: casual) -> "Can you help me with this?"
- "Bonjour, c'est quoi la deadline pour ce projet? Cordialement" (tone: formal) -> "Bonjour, Pourriez-vous me préciser la date limite pour ce projet, s’il vous plaît ? Cordialement."
- "Si ça ressemble beaucoup" (tone: confident) -> "Si, ça ressemble beaucoup !"
- "Ecoute je pense pas que ca soit trop importante" (tone: casual) -> "Écoute, je pense pas que ce soit très important"
"""

    messages = [
        SystemMessage(content=system_prompt_content),
        HumanMessage(content=user_text),
    ]

    try:
        logger.info(f"Processing with mode: {correction_mode}, tone: {desired_tone}")
        response = llm.invoke(messages)
        corrected_text = response.content.strip() if hasattr(response, 'content') else str(response).strip()
        
        # Remove quotes if they wrap the entire response
        if corrected_text.startswith('"') and corrected_text.endswith('"'):
            corrected_text = corrected_text[1:-1]
        
        logger.info(f"LLM response: {corrected_text[:100]}...")
        return corrected_text
    except Exception as e:
        logger.error(f"Error during LLM invocation: {e}")
        return "Sorry, I encountered an error while processing your message."

# --- Keyboard Generators ---
def get_tone_keyboard():
    """Generate inline keyboard for tone selection."""
    keyboard = []
    # Create 2 columns of tone buttons
    tone_keys = list(TONE_PRESETS.keys())
    for i in range(0, len(tone_keys), 2):
        row = []
        for j in range(2):
            if i + j < len(tone_keys):
                key = tone_keys[i + j]
                row.append(InlineKeyboardButton(
                    key.title(), 
                    callback_data=f"tone_{key}"
                ))
        keyboard.append(row)
    
    # Add custom tone and back buttons
    keyboard.append([
        InlineKeyboardButton("✏️ Custom Tone", callback_data="tone_custom"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_correction_mode_keyboard():
    """Generate inline keyboard for correction mode selection."""
    keyboard = [
        [
            InlineKeyboardButton("📝 Full Correction", callback_data="mode_full"),
            InlineKeyboardButton("📖 Grammar Only", callback_data="mode_grammar_only")
        ],
        [
            InlineKeyboardButton("🎨 Style Only", callback_data="mode_style_only"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_quick_actions_keyboard():
    """Generate quick action buttons for processed messages."""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Try Different Tone", callback_data="change_tone"),
            InlineKeyboardButton("⚙️ Different Mode", callback_data="change_mode")
        ],
        [
            InlineKeyboardButton("🔄 Reprocess Message", callback_data="reprocess_last")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced start command with feature overview."""
    welcome_text = """
🤖 **Grammar & Style Correction Bot**

✨ **Features:**
• Automatic grammar and spelling correction
• Tone adjustment (professional, friendly, formal, etc.)
• Multiple correction modes
• Multi-language support

🎯 **How to use:**
1. Just send me any message to get it corrected
2. Use `/tone` to change the correction tone
3. Use `/mode` to switch correction modes
4. Use `/settings` to view your current preferences

📝 **Quick Commands:**
• `/tone` - Choose correction tone
• `/mode` - Select correction mode  
• `/settings` - View current settings
• `/help` - Show this message

Ready to improve your messages! 🚀
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def tone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show tone selection keyboard."""
    await update.message.reply_text(
        "🎨 Choose your preferred tone:",
        reply_markup=get_tone_keyboard()
    )

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show correction mode selection keyboard."""
    await update.message.reply_text(
        "⚙️ Choose correction mode:",
        reply_markup=get_correction_mode_keyboard()
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current user settings."""
    current_tone = context.user_data.get('desired_tone', 'neutral and professional')
    current_mode = context.user_data.get('correction_mode', 'full')
    
    settings_text = f"""
⚙️ **Your Current Settings:**

🎨 **Tone:** {current_tone}
📝 **Mode:** {current_mode.replace('_', ' ').title()}

Use `/tone` to change tone or `/mode` to change correction mode.
"""
    await update.message.reply_text(settings_text, parse_mode='Markdown')

# --- Callback Handlers ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("tone_"):
        if data == "tone_custom":
            context.user_data['awaiting_custom_tone'] = True
            await query.edit_message_text(
                "✏️ Please type your custom tone (e.g., 'sarcastic and witty', 'empathetic and supportive'):"
            )
        else:
            tone_key = data.replace("tone_", "")
            if tone_key in TONE_PRESETS:
                context.user_data['desired_tone'] = TONE_PRESETS[tone_key]
                await query.edit_message_text(
                    f"✅ Tone set to: **{tone_key.title()}**\n\nNow send me a message to correct!",
                    parse_mode='Markdown'
                )
    
    elif data.startswith("mode_"):
        mode = data.replace("mode_", "")
        context.user_data['correction_mode'] = mode
        mode_name = mode.replace('_', ' ').title()
        await query.edit_message_text(
            f"✅ Correction mode set to: **{mode_name}**\n\nNow send me a message to process!",
            parse_mode='Markdown'
        )
    
    elif data == "change_tone":
        await query.edit_message_text(
            "🎨 Choose a different tone:",
            reply_markup=get_tone_keyboard()
        )
    
    elif data == "change_mode":
        await query.edit_message_text(
            "⚙️ Choose a different correction mode:",
            reply_markup=get_correction_mode_keyboard()
        )
    
    elif data == "reprocess_last":
        # Reprocess the last message with current settings
        if 'last_original' in context.user_data:
            original_text = context.user_data['last_original']
            desired_tone = context.user_data.get('desired_tone', "neutral and professional")
            correction_mode = context.user_data.get('correction_mode', "full")
            
            await query.edit_message_text("🔄 Reprocessing your message...")
            
            corrected_message = get_corrected_text(original_text, desired_tone, correction_mode)
            
            if corrected_message:
                # Check if there's a meaningful difference
                if corrected_message.strip().lower() == original_text.strip().lower():
                    response_text = f"✅ **No changes needed!**\n\n📝 **Your message:** {original_text}"
                else:
                    response_text = f"✨ **Corrected version:**\n\n{corrected_message}"
                
                context.user_data['last_corrected'] = corrected_message
                
                await query.edit_message_text(
                    response_text,
                    parse_mode='Markdown',
                    reply_markup=get_quick_actions_keyboard()
                )
            else:
                await query.edit_message_text("❌ Sorry, I couldn't reprocess your message.")
        else:
            await query.edit_message_text("❌ No previous message to reprocess.")
    
    elif data == "cancel":
        await query.edit_message_text("❌ Cancelled.")

# --- Message Handler ---
@rate_limit(max_calls=10, time_window=60)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced message handler with better response formatting."""
    user_message_text = update.message.text
    chat_id = update.message.chat_id
    user_id = update.effective_user.id

    if not user_message_text:
        return

    # Handle custom tone input
    if context.user_data.get('awaiting_custom_tone'):
        context.user_data['desired_tone'] = user_message_text
        context.user_data['awaiting_custom_tone'] = False
        await update.message.reply_text(
            f"✅ Custom tone set to: **{user_message_text}**\n\nNow send me a message to correct!",
            parse_mode='Markdown'
        )
        return

    logger.info(f"Received message from {user_id}: {user_message_text[:100]}...")

    # Get user preferences
    desired_tone = context.user_data.get('desired_tone', "neutral and professional")
    correction_mode = context.user_data.get('correction_mode', "full")
    
    logger.info(f"Processing with tone: '{desired_tone}', mode: '{correction_mode}'")

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Process the message
    corrected_message = get_corrected_text(user_message_text, desired_tone, correction_mode)

    if corrected_message:
        # Store the messages for potential reprocessing
        context.user_data['last_original'] = user_message_text
        context.user_data['last_corrected'] = corrected_message
        
        # Simply return the corrected message - clean and fast
        await update.message.reply_text(
            corrected_message,
            reply_markup=get_quick_actions_keyboard()
        )
    else:
        await update.message.reply_text("❌ Sorry, I couldn't process your message. Please try again.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced error handler with more details."""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)

def main() -> None:
    """Start the enhanced bot."""
    # Initialize LLM on startup
    initialize_llm()
    if not llm:
        logger.error("LLM could not be initialized. Bot cannot start.")
        return

    # Create the Application
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("tone", tone_command))
    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("settings", settings_command))

    # Callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Message handler with rate limiting
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting enhanced grammar bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
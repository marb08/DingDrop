import os
import sys
import logging
import requests
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters, ContextTypes

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

URL_RECEIVED, TAGS_INPUT, SERVICE_SELECTION = range(3)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")
LINKDING_URL = os.getenv("LINKDING_URL")
LINKDING_API_TOKEN = os.getenv("LINKDING_API_TOKEN")
READECK_API_URL = os.getenv("READECK_API_URL")
READECK_API_TOKEN = os.getenv("READECK_API_TOKEN")
TOPIC_ID = int(os.getenv("TOPIC_ID", "0"))  # If TOPIC_ID env variable is not present, then this value is "0"

required_vars = {
    "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
    "MY_CHAT_ID": MY_CHAT_ID,
    "LINKDING_URL": LINKDING_URL,
    "LINKDING_API_TOKEN": LINKDING_API_TOKEN,
    "READECK_API_URL": READECK_API_URL,
    "READECK_API_TOKEN": READECK_API_TOKEN
}

for var_name, var_value in required_vars.items():
    if not var_value:
        logger.error(f"Missing required environment variable: {var_name}")
        sys.exit(1)

def chat_id_restricted(func):
    """Decorator to restrict bot access to specific chat ID and topic ID."""
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        allowed_chat_id = int(MY_CHAT_ID)
        allowed_topic_id = int(TOPIC_ID)

        chat_id = update.effective_chat.id
        topic_id = update.message.message_thread_id if update.message else None

        logger.info(f"Received message in chat ID: {chat_id}, topic ID: {topic_id}")

        if chat_id != allowed_chat_id:
            logger.warning(f"Unauthorized access attempt in chat {chat_id}")
            await update.message.reply_text("Sorry, I only respond to my owner.")
            return

        if allowed_topic_id != 0 and topic_id != allowed_topic_id:
            logger.warning(f"Message received in unauthorized topic {topic_id}")
            await update.message.reply_text("❌ This topic is not authorized.")
            return

        return await func(update, context, *args, **kwargs)

    return wrapped

@chat_id_restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! Send me a URL to save it.")

@chat_id_restricted
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message_text = update.message.text
    url_match = re.search(r'(http[s]?://[^\s]+)', message_text)

    if url_match:
        url = url_match.group(0)
        context.user_data['url'] = url
        
        keyboard = [
            [InlineKeyboardButton("📌 Linkding", callback_data='linkding')],
            [InlineKeyboardButton("📖 Readeck", callback_data='readeck')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ URL received: {url}\nSelect a service to use:",
            reply_markup=reply_markup
        )
        return SERVICE_SELECTION
    else:
        await update.message.reply_text("❌ Error parsing the message. Please send a valid URL.")
        return ConversationHandler.END

@chat_id_restricted
async def service_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    service = query.data
    context.user_data['service'] = service
    
    await query.edit_message_text(
        "📩 Send tags (comma-separated) or /skip to save without tags."
    )
    return TAGS_INPUT

@chat_id_restricted
async def handle_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        url = context.user_data['url']
        service = context.user_data['service']
        tags = []

        if update.message.text.lower() != '/skip':
            tags = [tag.strip() for tag in update.message.text.split(',')]

        if service == 'linkding':
            data = {'url': url, 'tag_names': tags}
            headers = {'Authorization': f'Token {LINKDING_API_TOKEN}', 'Content-Type': 'application/json'}
            response = requests.post(f"{LINKDING_URL}/api/bookmarks/", json=data, headers=headers)
        elif service == 'readeck':
            data = {'url': url, 'labels': tags}
            headers = {'Authorization': f'Bearer {READECK_API_TOKEN}', 'Content-Type': 'application/json'}
            print(data)
            print(headers)
            print(f"{READECK_API_URL}/api/bookmarks")
            response = requests.post(f"{READECK_API_URL}/api/bookmarks", json=data, headers=headers)
        
        if response.status_code in [202, 201]:
            await update.message.reply_text(f"✅ Bookmark successfully saved to {service.capitalize()}! 📌")
        else:
            await update.message.reply_text(f"❌ Failed to save bookmark to {service.capitalize()}.")
            logger.error(f"{service.capitalize()} API error: {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await update.message.reply_text("An unexpected error occurred. Please try again.")
    finally:
        context.user_data.clear()
    return ConversationHandler.END

@chat_id_restricted
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main() -> None:
    logger.info("Starting bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)],
        states={
            SERVICE_SELECTION: [CallbackQueryHandler(service_selection)],
            TAGS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tags), CommandHandler("skip", handle_tags)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    logger.info("Bot is ready")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)

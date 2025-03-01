import os
import sys
import logging
import requests, subprocess
import re
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation
URL_RECEIVED, TAGS_INPUT = range(2)

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")
LINKDING_URL = os.getenv("LINKDING_URL")
LINKDING_API_TOKEN = os.getenv("LINKDING_API_TOKEN")



# Validate required environment variables
required_vars = {
    "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
    "MY_CHAT_ID": MY_CHAT_ID,
    "LINKDING_URL": LINKDING_URL,
    "LINKDING_API_TOKEN": LINKDING_API_TOKEN
}

for var_name, var_value in required_vars.items():
    if not var_value:
        logger.error(f"Missing required environment variable: {var_name}")
        sys.exit(1)

def chat_id_restricted(func):
    """Decorator to restrict bot access to specific chat ID"""
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if str(update.effective_chat.id) != MY_CHAT_ID and str(update.effective_user.id) != MY_CHAT_ID:
            logger.warning(f"Unauthorized access attempt from {update.effective_user.id} in chat {update.effective_chat.id}")
            await update.message.reply_text("Sorry, I only respond to my owner.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

@chat_id_restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    await update.message.reply_text(
        "Welcome! Send me a URL to save it to Linkding."
    )

@chat_id_restricted
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle received URL"""
    message_text = update.message.text

    # Search for a URL anywhere in the message
    url_match = re.search(r'(http[s]?://[^\s]+)', message_text)

    # If a URL is found, proceed
    if url_match:
        url = url_match.group(0)
        context.user_data['url'] = url
        await update.message.reply_text(
            f"✅ URL received: {url}.\n📩 Send tags (comma-separated) or /skip to save without tags."
        )
        return TAGS_INPUT
    else:
        # If no URL is found, ask for a valid URL
        await update.message.reply_text("❌ Error parsing the message. Please send a valid URL.")
        return ConversationHandler.END

@chat_id_restricted
async def handle_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle tags and save bookmark to Linkding"""
    try:
        url = context.user_data['url']
        tags = []

        # If user provided tags, split and clean them
        if update.message.text.lower() != '/skip':
            tags = [tag.strip() for tag in update.message.text.split(',')]

        # Prepare data for Linkding API
        data = {
            'url': url,  # URL provided by the user
            'tag_names': tags  # 'labels' instead of 'tags'
        }

        headers = {
            'Authorization': f'Token {LINKDING_API_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Send the request to Linkding API
        response = requests.post(f"{LINKDING_URL}/api/bookmarks/", json=data, headers=headers)

        if response.status_code == 201:
            await update.message.reply_text("✅ Bookmark successfully saved to Linkding! 📌")
        elif response.status_code == 401:
            # Handle Unauthorized error (401)
            await update.message.reply_text("⛔ Authorization failed. Please check your API token.")
            logger.error(f"Linkding API 401 Unauthorized: {response.text}")
        else:
            # For other non-success responses
            await update.message.reply_text("❌ Failed to save bookmark to Linkding.\nPlease check your logs for troubleshooting.")
            logger.error(f"Linkding API error: {response.text}")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await update.message.reply_text("An unexpected error occurred. Please try again.")
    finally:
        context.user_data.pop('url', None)  # Clean up user data

    return ConversationHandler.END


@chat_id_restricted
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main() -> None:
    """Start the bot"""
    try:
        logger.info("Starting bot...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)],
            states={
                TAGS_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tags),
                    CommandHandler("skip", handle_tags)
                ]
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(conv_handler)

        logger.info("Bot is ready to handle messages")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
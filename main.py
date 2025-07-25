import os
import asyncio
import logging
from dotenv import load_dotenv
from typing import Any

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
    Application
)

# Load .env variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Validate environment variables
REQUIRED_ENV_VARS = ["BOT_TOKEN", "WEB_APP_URL"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

BOT_TOKEN: str = os.getenv("BOT_TOKEN")  # type: ignore
WEB_APP_URL: str = os.getenv("WEB_APP_URL")  # type: ignore

# Handler for /start command
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Open HOS App",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="Welcome to the HOS Support App!\nClick the button below to open the HOS App.",
        reply_markup=reply_markup
    )

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

# Startup function
async def start_bot() -> None:
    application: Application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_error_handler(error_handler)

    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("Bot started. Listening for messages...")

    try:
        await asyncio.Event().wait()  # Run forever
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down bot...")
        await application.stop()
        await application.shutdown()

# Entrypoint
if __name__ == "__main__":
    asyncio.run(start_bot())

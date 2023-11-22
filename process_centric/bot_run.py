#!/usr/bin/env python

"""
FlashMinds revolutionizes the way you learn by combining the simplicity of flashcards with the power of artificial intelligence. 
In addition to traditional flashcard functionality, FlashMinds employs advanced AI algorithms to enhance your learning experience.

Usage:
Press Ctrl-C on the command line or send a signal to stop the bot."
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot_manager import help, start, unknown

#Load environment variables from the .env file
load_dotenv()

#Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def set_handlers(bot):
    bot.add_handler(CommandHandler('help', help))
    bot.add_handler(CommandHandler('start', start))
    bot.add_handler(MessageHandler(filters.COMMAND, unknown))

def main():
    #Retrieve the API token from the environment variable
    TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
    if TELEGRAM_API_TOKEN is None:
        raise Exception("No API token found. Please check your .env file.")

    #Create the Application and pass it bot's token.
    bot = Application.builder().token(TELEGRAM_API_TOKEN).build()

    #Set command handlers
    set_handlers(bot)

    #Run the bot until the user presses Ctrl-C
    bot.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
    main()


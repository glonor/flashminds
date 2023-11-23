#!/usr/bin/env python

"""
FlashMinds revolutionizes the way you learn by combining the simplicity of flashcards with the power of artificial intelligence. 
In addition to traditional flashcard functionality, FlashMinds employs advanced AI algorithms to enhance your learning experience.

Usage:
Press Ctrl-C on the command line or send a signal to stop the bot."
"""

import os
import logging, requests, textwrap
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes
from bot_manager import help, start, unknown
from deck_manager import cancel, button_click, write_answer, write_question, set_deck_name, add, decks

CHOOSING, MENU, QUESTION, ANSWER = range(4)

#Load environment variables from the .env file
load_dotenv()

#Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logging.getLogger('telegram.ext.conversationhandler').setLevel(logging.DEBUG)
#logging.getLogger("httpx").setLevel(logging.INFO)
logger = logging.getLogger(__name__)
    
def main():
    #Retrieve the API token from the environment variable
    TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
    if TELEGRAM_API_TOKEN is None:
        raise Exception("No API token found. Please check your .env file.")

    #Create the Application and pass it bot's token.
    bot = Application.builder().token(TELEGRAM_API_TOKEN).build()


    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT, set_deck_name)],
            QUESTION: [MessageHandler(filters.TEXT, write_question)],
            ANSWER: [MessageHandler(filters.TEXT, write_answer)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )


    #Set commands handler
    bot.add_handler(conversation_handler)
    bot.add_handler(CommandHandler('help', help))
    bot.add_handler(CommandHandler('start', start))
    bot.add_handler(MessageHandler(filters.COMMAND, unknown))

    #Set button handler
    bot.add_handler(CallbackQueryHandler(button_click))

    #Run the bot until the user presses Ctrl-C
    bot.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
    main()


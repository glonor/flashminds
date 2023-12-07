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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes

from handlers.bot_manager import *

from handlers.decks_manager import *
from handlers.study_manager import *
from handlers.remove_manager import *
from handlers.add_manager import *


NAME, OPTION, QUESTION, ANSWER, IMAGE, REGENERATE = range(6)  #state - conversation_handler_add
SELECTION, OPTION, START, CARD, RATING = range(5) #state - conversation_handler_study
PRINT = range(1) #state - conversation_handler_decks
REMOVE = range(1) #state - conversation_handler_remove

#Load environment variables from the .env file
TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_TOKEN')


#Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO) #Levels: CRITICAL, ERROR, WARNING, INFO
logger = logging.getLogger(__name__)
    
def main():
    #Retrieve the API token from the environment variable
    if TELEGRAM_API_TOKEN is None:
        raise Exception("No API token found. Please check your .env file.")

    #Create the Application and pass it bot's token.
    bot = Application.builder().token(TELEGRAM_API_TOKEN).build()

    #Set structure conversation handler /add command
    conversation_handler_add = ConversationHandler(
        entry_points=[
            CommandHandler('add', add),
            MessageHandler(filters.Regex("^(✚ New Deck)$"), add)
        ],
        states={
            NAME: [MessageHandler(filters.TEXT, study_add_name)],
            OPTION: [MessageHandler(filters.TEXT, study_input_opt)],
            QUESTION: [MessageHandler(filters.TEXT, study_set_question)],
            ANSWER: [MessageHandler(filters.TEXT, study_set_answer)],
            IMAGE: [MessageHandler(filters.PHOTO | filters.Document.ALL, study_set_card_from_image)],
            REGENERATE: [MessageHandler(filters.TEXT, study_regenerate_card_from_image)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    
    #Set structure conversation handler /study command
    conversation_handler_study = ConversationHandler(
        entry_points=[
            CommandHandler('study', study),
            MessageHandler(filters.Regex("^(✨ Start a session ✨)$"), study)
        ],
        states={
            SELECTION: [MessageHandler(filters.TEXT, study_deck_selection)],
            OPTION: [MessageHandler(filters.TEXT, study_session_option)],
            START: [MessageHandler(filters.TEXT, study_session_start)],
            CARD: [MessageHandler(filters.TEXT, study_session_card)],
            RATING: [MessageHandler(filters.TEXT, study_rating_answer)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    #Set structure conversation handler /decks command
    conversation_handler_decks = ConversationHandler(
        entry_points=[
            CommandHandler('decks', decks),
            MessageHandler(filters.Regex("^(📚 Decks)$"), decks)
        ],
        states={
            PRINT: [MessageHandler(filters.TEXT, decks_deck_selection)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    
    #Set structure conversation handler /remove command
    conversation_handler_remove = ConversationHandler(
        entry_points=[
            CommandHandler('remove', remove),
            MessageHandler(filters.Regex("^(🗑️ Remove)$"), remove)
        ],
        states={
            REMOVE: [MessageHandler(filters.TEXT, remove_deck_selection)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    #Set command /start
    bot.add_handler(CommandHandler('start', start))

    #Set command /help
    bot.add_handler(CommandHandler('help', help))

    #Set conversation_handler /add
    bot.add_handler(conversation_handler_add)
    bot.add_handler(conversation_handler_decks)
    bot.add_handler(conversation_handler_study)
    bot.add_handler(conversation_handler_remove)


    #Set unknown command handler
    bot.add_handler(MessageHandler(filters.COMMAND, unknown))

    #Run the bot until the user presses Ctrl-C
    bot.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
    main()


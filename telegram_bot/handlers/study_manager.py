from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import ContextTypes
import requests, textwrap
import os 
from io import BytesIO

from handlers.bot_manager import *

BL_API_BASE_URL = "http://localhost:5000"
GPT_API_BASE_URL = "http://localhost:5002"

SELECTION, START = range(2)

# ---------------------------------------------------------------- #
# ---------------------  HANDLER /STUDY COMMAND ------------------ #
# ---------------------------------------------------------------- #

#1 ---- choose deck
async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    get_decks_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks"

    #user deck list
    get_decks_res = requests.get(get_decks_endpoint, timeout=10)

    if get_decks_res.status_code == 200:  #list deck ok
        response_data = get_decks_res.json()
        decks = response_data.get('decks', [])

        if not decks: #empty list
            msg="👀 No decks are present. You can create one with the command /add"
            reply_markup = await show_keyboard(update, context)
            await update.message.reply_text(msg, reply_markup=reply_markup)

        else:
            keyboard=[]

            for deck in decks:
                deck_id = deck.get('deck_id')
                deck_name = deck.get('deck_name')
                flashcard_count = deck.get('flashcard_count')

                if flashcard_count >= 1:
                    button = InlineKeyboardButton(f"{deck_name} - Cards: {flashcard_count}", callback_data=f"study_deck_{deck_id}")
                    keyboard.append([button])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("📚 Welcome to the Study Section!\n\nLet's dive into the world of knowledge and enhance your learning.\nTo get started, please choose a deck to study:", reply_markup=reply_markup)
            
    else:  #error
        msg = f"Internal error. Status code: {get_decks_res.status_code}"
        await update.message.reply_html(text=msg)
        return 
    
    return SELECTION

#2 ---- #chatgpt or normal
async def study_deck_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_answer = query.data
    user = update.effective_user
    deck_id = int(query.data.split("_")[2])  #ID extraction
    
    context.user_data['study_deck_id'] = deck_id

    keyboard = [
            [InlineKeyboardButton("Use ChatGPT to generate flashcards", callback_data='chatgpt')],
            [InlineKeyboardButton("Use your own custom flahcards", callback_data='normal')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Great choice! Now, let's decide how you'd like to proceed:", reply_markup=reply_markup)   

    return START
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import ContextTypes
import requests, textwrap
import os 
from io import BytesIO

from handlers.bot_manager import *

DECK, INPUT, IMAGE, REGENERATE, QUESTION, ANSWER = range(6)

BL_API_BASE_URL = "http://localhost:5000"
GPT_API_BASE_URL = "http://localhost:5002"
OCR_API_BASE_URL = "http://localhost:5003"

# ---------------------------------------------------------------- #
# -------------------  HANDLER /REMOVE COMMAND ------------------- #
# ---------------------------------------------------------------- #

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

                button = InlineKeyboardButton(f"{deck_name} - Cards: {flashcard_count}", callback_data=f"remove_deck_{deck_id}")
                keyboard.append([button])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🗑️ Choose the deck you want to remove", reply_markup=reply_markup)
            

    else:  #error
        msg = f"Internal error. Status code: {get_decks_res.status_code}"
        await update.message.reply_html(text=msg)

#1 ---- remove specific deck
async def remove_deck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_answer = query.data
    user = update.effective_user
    deck_id = int(query.data.split("_")[2])  #ID extraction

    remove_deck_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks/{deck_id}"
    remove_deck_res = requests.delete(remove_deck_endpoint, timeout=10)

    if remove_deck_res.status_code == 200: #success
        await update.callback_query.message.edit_text("🚮 Deck deleted successfully")
    
    else:
        await update.callback_query.message.edit_text(f"Internal error. Status code: {remove_deck_res.status_code}")

# ---------------------------------------------------------------- #
# ---------------------  REPLY KEYBOARD MENU  -------------------- #
# ---------------------------------------------------------------- #

async def show_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("✨ Start a session ✨")],
        [KeyboardButton("📚 Decks"), KeyboardButton("✚ New Deck"), KeyboardButton("🗑️ Remove")]
    ]

    #Store keyboard in the context
    menu = ReplyKeyboardMarkup(keyboard, resize_keyboard= True)
    return menu
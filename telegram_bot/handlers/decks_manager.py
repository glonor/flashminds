from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import ContextTypes
import requests, textwrap
import os 
from io import BytesIO

from handlers.bot_manager import *

BL_API_BASE_URL = "http://localhost:5000"
SC_API_BASE_URL = "http://localhost:5001"
GPT_API_BASE_URL = "http://localhost:5002"

# ---------------------------------------------------------------- #
# ---------------------  HANDLER /DECKS COMMAND ------------------ #
# ---------------------------------------------------------------- #

async def decks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    get_decks_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks"

    #user deck list
    get_decks_res = requests.get(get_decks_endpoint, timeout=10)

    if get_decks_res.status_code == 200:  #list deck
        response_data = get_decks_res.json()
        decks = response_data.get('decks', [])

        if not decks: #empty list
            msg="👀 No decks are present. You can create one with the command /add"
            reply_markup = await show_keyboard(update, context)
            await update.message.reply_text(msg, reply_markup=reply_markup)

        else:
            msg="🪄 As requested, here's a list of your decks:\n"

            for deck in decks:
                deck_id = deck.get('deck_id')
                deck_name = deck.get('deck_name')
                flashcard_count = deck.get('flashcard_count')
                deck_rating = deck.get('last_average_confidence')

                msg += f"\n ➡️ <b>{deck_name}</b> - 📚 {flashcard_count} - ⭐️ {deck_rating}"

            reply_markup = await show_keyboard(update, context)
            await update.message.reply_html(msg, reply_markup=reply_markup)

    else:  #error
        msg = f"Internal error. Status code: {get_decks_res.status_code}"
        await update.message.reply_html(text=msg)

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
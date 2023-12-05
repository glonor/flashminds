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

SELECTION = range(1) #state - conversation_handler_decks

# ---------------------------------------------------------------- #
# ---------------------  HANDLER /DECKS COMMAND ------------------ #
# ---------------------------------------------------------------- #

async def decks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  #telegram user
    get_decks_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks" #decks endpoint

    #List of user decks
    get_decks_res = requests.get(get_decks_endpoint, timeout=10)

    if get_decks_res.status_code == 200:  #success
        response_data = get_decks_res.json()
        decks = response_data.get('decks', [])

        if not decks:  #empty list
            msg = "👀 No decks are present. You can create one with the command /add"
            reply_markup = await show_keyboard(update, context)
            await update.message.reply_text(msg, reply_markup=reply_markup)

        else:
            deck_array = []  #Initialize an array to store decks
            keyboard = []  #Initialize reply keyboard

            for deck in decks:
                deck_id = deck.get('deck_id')
                deck_name = deck.get('deck_name')
                flashcard_count = deck.get('flashcard_count')

                if flashcard_count >= 1:
                    button = KeyboardButton(f"{deck_name} [Cards: {flashcard_count}]")
                    keyboard.append([button])
                    deck_array.append({'id': deck_id, 'name': deck_name})

            context.user_data['deck_array'] = deck_array

            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text("🪄As requested, here is a list of your decks. Select one to see what it contains 👀", reply_markup=reply_markup)

    else:  #error
        reply_markup = await show_keyboard(update, context)
        msg = f"Internal error. Status code: {get_decks_res.status_code}"
        await update.message.reply_html(text=msg, reply_markup=reply_markup)
        context.user_data.clear()
        return ConversationHandler.END #loop exit

    return SELECTION

#2 ---- Deck id check
async def decks_deck_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    deck_name = update.message.text #input user
    deck_array = context.user_data['deck_array']

    #Check if the user input is in the deck_array
    selected_deck = next((deck for deck in deck_array if deck_name.startswith(deck['name'])), None)

    if selected_deck: #deck present in array
        #TODO: show card
        context.user_data['study_deck_id'] = selected_deck['id']
        get_decks_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks/{context.user_data['study_deck_id']}/flashcards" #decks cards

        #List of cards
        get_decks_res = requests.get(
            get_decks_endpoint
        )

        if get_decks_res.status_code == 200:  #flashcard ok
            response_data = get_decks_res.json()

            flashcards = response_data.get('flashcards', [])
            if not flashcards:
                message = "No flashcards found."
            else:
                message = f"📚 Flashcards - Deck {selected_deck['name']}:\n"
                for card in flashcards:
                    question = card.get('question')
                    answer = card.get('answer')
                    message += f"\n<b>Q:</b> {question}\n<b>A:</b> {answer}\n"

            reply_markup = await show_keyboard(update, context)
            await update.message.reply_html(text=message, reply_markup=reply_markup)
            
        else: #error
            reply_markup = await show_keyboard(update, context)
            msg = f"Internal error. Status code: {next_flashcard_res.status_code}"
            await update.message.reply_html(text=msg, reply_markup=reply_markup)
            context.user_data.clear()
            return ConversationHandler.END #session exit

    else: #deck not valid
        await update.message.reply_text(f"Repeat the choice.")
        return SELECTION

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
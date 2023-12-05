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

SELECTION, OPTION, START, CARD, RATING = range(5) #state - conversation_handler_study

# ---------------------------------------------------------------- #
# ---------------------  HANDLER /STUDY COMMAND ------------------ #
# ---------------------------------------------------------------- #

#1 ---- Deck Selection
async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
            await update.message.reply_text("📚 I'm ready. Tell me which deck you want to use for the study session.", reply_markup=reply_markup)

    else:  #error
        reply_markup = await show_keyboard(update, context)
        msg = f"Internal error. Status code: {get_decks_res.status_code}"
        await update.message.reply_html(text=msg, reply_markup=reply_markup)
        context.user_data.clear()
        return ConversationHandler.END #loop exit

    return SELECTION

#2 ---- Deck id check
async def study_deck_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    deck_name = update.message.text #input user
    deck_array = context.user_data['deck_array']

    #Check if the user input is in the deck_array
    selected_deck = next((deck for deck in deck_array if deck_name.startswith(deck['name'])), None)

    if selected_deck: #deck present in array
        context.user_data['study_deck_id'] = selected_deck['id']
        keyboard = [
            [KeyboardButton("Yes, use AI")], 
            [KeyboardButton("No, use my cards")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
        await update.message.reply_text(
            f"Great choice! You selected the deck: {selected_deck['name']}.\n"
            f"Now decide if you want to use the power of AI during your study session ✨🪄", 
            reply_markup=reply_markup
        )

    else: #deck not valid
        await update.message.reply_text(f"Repeat the choice.")
        return SELECTION
    
    return OPTION

#3 ---- Chatgpt or Normal selection
async def study_session_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    option = update.message.text #input user

    #save user decision
    if option == "Yes, use AI": 
        context.user_data['study_gen_opt'] = True

    elif option == "No, use my cards":
        context.user_data['study_gen_opt'] = False

    else: #option not valid, repeat
        keyboard = [
            [KeyboardButton("Yes, use AI")], 
            [KeyboardButton("No, use my cards")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
        await update.message.reply_text(f"Repeat the choice.", reply_markup=reply_markup)
        return OPTION

    keyboard = [
        [KeyboardButton("🚥 START")], 
        [KeyboardButton("🏁 STOP")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
    await update.message.reply_text(f"Buckle up, press START to begin your study session! 📖", reply_markup=reply_markup)
    context.user_data['study_session_id'] = ""

    return START

#4 ---- Start Study Session | Another Card
async def study_session_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    option = update.message.text #input user

    if option == "🚥 START" or option == "Another one": 

        #check if session id is created
        if not context.user_data['study_session_id']:
            start_session_endpoint = f"{SC_API_BASE_URL}/start_study_session" #session endpoint
            start_session_res = requests.post(
                start_session_endpoint, 
                json={
                    "user_id": user.id, 
                    "deck_id": int(context.user_data['study_deck_id']) #deck_id
                }
            )

            if start_session_res.status_code == 201: #session created
                response_data = start_session_res.json()
                session_id = response_data.get('session_id', None)
                context.user_data['study_session_id'] = session_id 
            
            else: #error
                reply_markup = await show_keyboard(update, context)
                msg = f"Internal error. Status code: {start_session_res.status_code}"
                await update.message.reply_text(text=msg, reply_markup=reply_markup)
                context.user_data.clear()
                return ConversationHandler.END #exit

        #generate flashcard
        next_flashcard_endpoint = f"{SC_API_BASE_URL}/get_next_flashcard" #flashcard endpoint
        next_flashcard_res = requests.get(
            next_flashcard_endpoint, 
            json={
                "user_id": user.id, 
                "deck_id": context.user_data['study_deck_id'], 
                "session_id": context.user_data['study_session_id'],
                "chatgpt": context.user_data['study_gen_opt'] #boolean
            }
        )
   
        if next_flashcard_res.status_code == 200:  #flashcard ok
            response_data = next_flashcard_res.json()
            #card_id
            card_id = response_data.get('card_id', None)
            context.user_data['study_card_id'] = card_id 
            #question
            question = response_data.get('question', None)
            #answer 
            answer = response_data.get('answer', None)
            context.user_data['study_card_answer'] = answer
                
            keyboard = [
                [KeyboardButton("View answer 👀")],
            ]
                
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
            await update.message.reply_text(text=question, reply_markup=reply_markup)
            return CARD
            
        else: #error
            reply_markup = await show_keyboard(update, context)
            msg = f"Internal error. Status code: {next_flashcard_res.status_code}"
            await update.message.reply_html(text=msg, reply_markup=reply_markup)
            context.user_data.clear()
            return ConversationHandler.END #session exit

    elif option == "🏁 STOP":
        
        #check if session id is created
        if(context.user_data['study_session_id'] == ""):
            reply_markup = await show_keyboard(update, context)
            msg = f"Oh, no study? It'll be for next time. I'll wait for you. 😌"
            await update.message.reply_html(text=msg, reply_markup=reply_markup)
            context.user_data.clear()
            return ConversationHandler.END #loop exit
        
        else: #session_id exist

            stop_session_endpoint = f"{SC_API_BASE_URL}/end_study_session" #session endpoint
            stop_session_res = requests.post(
                stop_session_endpoint, 
                json={
                    "user_id": user.id, 
                    "deck_id": context.user_data['study_deck_id'], 
                    "session_id": context.user_data['study_session_id'],
                }
            )

            if stop_session_res.status_code == 200:  #session stop ok
                response_data = stop_session_res.json()
                average_confidence = response_data.get('average_confidence', None) #avg confidence session

                reply_markup = await show_keyboard(update, context)
                await update.message.reply_text(
                    text=f"Perfect! Your study session is over. The average score is {average_confidence}. Don't give up, see you next time. 👋🏻", reply_markup=reply_markup)
                context.user_data.clear()
                return ConversationHandler.END #loop exit

            else:
                reply_markup = await show_keyboard(update, context)
                msg = f"Internal error. Status code: {stop_session_res.status_code}"
                await update.message.reply_html(text=msg, reply_markup=reply_markup)
                context.user_data.clear()
                return ConversationHandler.END #session exit

    else: #option not valid
        keyboard = [
            [KeyboardButton("🚥 START")], 
            [KeyboardButton("🏁 STOP")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
        await update.message.reply_text(f"Repeat the choice.", reply_markup=reply_markup)
        return START

#5 ---- View Answer Card 
async def study_session_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    text = update.message.text #input user

    if (text == "View answer 👀"):
        keyboard = [
            [KeyboardButton("⭐️5"), KeyboardButton("⭐️4"), KeyboardButton("⭐️3"), KeyboardButton("⭐️2"), KeyboardButton("⭐️1")], 
        ] #reply rating keyboard

        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
        await update.message.reply_text(f"Answer:\n{context.user_data['study_card_answer']}\n\n How do you rate your answer?⭐️:", reply_markup=reply_markup)
        
    else: #option not valid
        keyboard = [
            [KeyboardButton("View answer 👀")], 
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
        await update.message.reply_text(f"Repeat the choice.", reply_markup=reply_markup)
        return CARD        
    
    return RATING

#6 ---- Rating Card | Call Another Card | Stop
async def study_rating_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    text = update.message.text #input user

    #function to check that stars are between 1 and 5
    def is_valid_rating(star_count):
        return 1 <= star_count <= 5

    #invalid message sent to user
    async def send_invalid_rating_message():
        keyboard = [
            [KeyboardButton("⭐️5"), KeyboardButton("⭐️4"), KeyboardButton("⭐️3"), KeyboardButton("⭐️2"), KeyboardButton("⭐️1")], 
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
        await update.message.reply_text("Rating not valid. Please repeat.", reply_markup=reply_markup)

    if text.startswith("⭐️") and len(text) == 3 and text[2].isdigit():
        star_count = int(text[2])  #Count the number of stars

        if is_valid_rating(star_count):
            rating_session_endpoint = f"{SC_API_BASE_URL}/review_flashcard" #rating endpoint
            rating_session_res = requests.post(
                rating_session_endpoint, 
                json={
                    "user_id": user.id, 
                    "deck_id": context.user_data['study_deck_id'], 
                    "session": context.user_data['study_session_id'],
                    "card_id": context.user_data['study_card_id'],
                    "confidence": star_count #number of stars
                }
            )

            if rating_session_res.status_code == 404:  #unsuccess
                reply_markup = await show_keyboard(update, context)
                msg = f"Internal error. Status code: {rating_session_res.status_code}"
                await update.message.reply_html(text=msg, reply_markup=reply_markup)
                context.user_data.clear()
                return ConversationHandler.END #session exit 

            keyboard = [
                [KeyboardButton("Another one")],
                [KeyboardButton("🏁 STOP")],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
            await update.message.reply_text("Rating saved. Now what can I do for you?", reply_markup=reply_markup)
            return START

        else:
            await send_invalid_rating_message()
            return RATING

    else:  #rating option not valid
        await send_invalid_rating_message()
        return RATING

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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import ContextTypes
import requests, textwrap
import os 
from io import BytesIO

from handlers.bot_manager import *

BL_API_BASE_URL = "http://localhost:5000"
GPT_API_BASE_URL = "http://localhost:5002"

SELECTION, START, SESSION_OPT, GENERATION, VIEW, RATING, MORE = range(7)

# ---------------------------------------------------------------- #
# ---------------------  HANDLER /STUDY COMMAND ------------------ #
# ---------------------------------------------------------------- #

#1 ---- deck choosing
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
            [InlineKeyboardButton("End study session", callback_data='stop')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Great choice! Now, let's decide how you'd like to proceed:", reply_markup=reply_markup)   

    return START

#3 ---- #start
async def study_gen_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_answer = query.data
    
    if user_answer == 'chatgpt':
        context.user_data['study_gen_opt'] = True

    elif user_answer == 'normal':
        context.user_data['study_gen_opt'] = False

    else:
        result_message="🛑 Study session cancelled."
        await update.callback_query.message.edit_text(result_message)
        context.user_data.clear()
        return ConversationHandler.END #loop exit

    keyboard = [
            [InlineKeyboardButton("START SESSION", callback_data='start')],
            [InlineKeyboardButton("End", callback_data='stop')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="📝 Great choice! Come on, click START 🤩", reply_markup=reply_markup)   

    return SESSION_OPT
    

async def study_session_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    query = update.callback_query
    user_answer = query.data

    start_session_endpoint = f"{BL_API_BASE_URL}/start_study_session"
    
    if user_answer == 'start':
        start_session_res = requests.post(
            start_session_endpoint, 
            json={
                "user_id": user.id, 
                "deck_id": context.user_data['study_deck_id'], 
            }
        )
        
        if start_session_res.status_code == 201:  #session created
            response_data = start_session_res.json()
            session_id = response_data.get('session_id', None)
            context.user_data['session_id'] = session_id
            return GENERATION
            
        else:
            msg = f"Internal error. Status code: {start_session_res.status_code}"
            await update.message.reply_html(text=msg)
            context.user_data.clear()
            return ConversationHandler.END #session exit
        
    else:
        result_message="🛑 Study session cancelled."
        await update.callback_query.message.edit_text(result_message)
        context.user_data.clear()
        return ConversationHandler.END #loop exit

async def study_card_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    
    next_flashcard_endpoint = f"{BL_API_BASE_URL}/get_next_flashcard"
    next_flashcard_res = requests.post(next_flashcard_endpoint, 
        json={
            "user_id": user.id, 
            "deck_id": context.user_data['study_deck_id'], 
            "session": context.user_data['session_id'],
            "chatgpt": context.user_data['study_gen_opt']
        }
    )

    if next_flashcard_res.status_code == 200:  #deck created
        response_data = next_flashcard_res.json()

        card_id = response_data.get('card_id', None)
        context.user_data['card_id'] = deck_id    
        answer = response_data.get('answer', None)
        context.user_data['answer'] = answer
        
        question = response_data.get('question', None)

        keyboard = [
                [
                    InlineKeyboardButton("View answer 👀", callback_data='answer')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text=question, reply_markup=reply_markup)
        return VIEW

    else:
        msg = f"Internal error. Status code: {create_endpoint_res.status_code}"
        await update.message.reply_html(text=msg)
        context.user_data.clear()
        return ConversationHandler.END #session exit

async def study_view_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  #telegram user
    query = update.callback_query
    user_answer = query.data

    if user_answer == 'view':
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data='1'),
                InlineKeyboardButton("2", callback_data='2'),
                InlineKeyboardButton("3", callback_data='3'),
                InlineKeyboardButton("4", callback_data='4'),
                InlineKeyboardButton("5", callback_data='5')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=context.user_data['answer'], reply_markup=reply_markup)
        return RATING 
    else:
        result_message="🛑 Internal error."
        await update.callback_query.message.edit_text(result_message)
        context.user_data.clear()
        return ConversationHandler.END #loop exit

async def study_rating_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_answer = int(query.data)

    if 1 <= user_answer <= 5: 
        rating_flashcard_endpoint = f"{BL_API_BASE_URL}/review_flashcard"
        rating_flashcard_res = requests.post(rating_flashcard_endpoint, 
            json={
                "user_id": user.id, 
                "deck_id": context.user_data['study_deck_id'], 
                "card_id": context.user_data['card_id'], 
                "session": context.user_data['session_id'],
                "confidence": user_answer
            }
        )

        if rating_flashcard_res.status_code == 200:  #rating ok
                response_data = rating_flashcard_res.json()

                keyboard = [
                        [InlineKeyboardButton("Another one", callback_data='more')],
                        [InlineKeyboardButton("Stop", callback_data='stop')],
                    ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(text="Flashcard reviewed successfully. Now?", reply_markup=reply_markup)
                return MORE

        else:
            msg = f"Internal error. Status code: {rating_flashcard_res.status_code}"
            await update.message.reply_html(text=msg)
            context.user_data.clear()
            return ConversationHandler.END #session exit


    else:
        result_message="🛑 Internal error."
        await update.callback_query.message.edit_text(result_message)
        context.user_data.clear()
        return ConversationHandler.END #loop exit

async def study_more_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_answer = int(query.data)

    if user_answer == 'more':
        return GENERATION

    else:
        stop_session_endpoint = f"{BL_API_BASE_URL}/end_study_session"
        stop_session_res = requests.post(
            create_session_endpoint, 
            json={
                "user_id": user.id, 
                "deck_id": context.user_data['study_deck_id'], 
                "session": context.user_data['session_id'],
            }
        )

        if stop_session_res.status_code == 200:  #rating ok
                response_data = stop_session_res.json()
                await update.message.reply_text(text="🛑 Study session done.")
                await update.callback_query.message.edit_text(result_message)
                context.user_data.clear()
                return ConversationHandler.END #loop exit

        else:
            msg = f"Internal error. Status code: {rating_flashcard_res.status_code}"
            await update.message.reply_html(text=msg)
            context.user_data.clear()
            return ConversationHandler.END #session exit

       




        
        if create_endpoint_res.status_code == 201:  #session created
            response_data = create_endpoint_res.json()
            session_id = response_data.get('session_id', None)
            context.user_data['session_id'] = session_id
            return GENERATION
            
        else:
            msg = f"Internal error. Status code: {create_endpoint_res.status_code}"
            await update.message.reply_html(text=msg)
            context.user_data.clear()
            return ConversationHandler.END #session exit
        
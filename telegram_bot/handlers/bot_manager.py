import textwrap
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
import requests
from os import environ

from handlers.deck_manager import *

#URL for the database
BL_API_BASE_URL = "http://localhost:5000"
#BL_API_BASE_URL = environ.get('DL_URL')


# ---------------------------------------------------------------- #
# ----------------------  HANDLER COMMANDS  ---------------------- #
# ---------------------------------------------------------------- #

#Handler /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram account data
    
    create_user_endpoint = f"{BL_API_BASE_URL}/users"
    create_user_res = requests.post(create_user_endpoint, json={"user_id": int(user.id), "username": str(user.full_name)})

    #Check if the user exists
    welcome_msg=""

    if create_user_res.status_code == 201: #user created
    
        welcome_msg = textwrap.dedent(
                f'''
                🚀 Hello {user.mention_html()}, Welcome to <b>FlashMinds</b>! 🧠
                Elevate your learning where smart flashcards meet AI magic! 📚✨

                🌟 Key Features:

                1️⃣ Smart Flashcards: Adaptive learning for your progress.

                2️⃣ Dynamic Wording: Varied concepts for deep understanding.

                3️⃣ Telegram Access: Study seamlessly via our intuitive bot.
                '''
            )        

    elif create_user_res.status_code == 409: #user already exist
        welcome_msg = textwrap.dedent(
            f'''
            🌟 Welcome back {user.mention_html()}! 🚀

            Embark on another session of enhanced learning with FlashMinds. 🧠✨ We're thrilled to have you back!
            '''
        )

    else: #error
        welcome_msg = f"Internal error. Status code: {create_user_res.status_code}"
    

    await show_keyboard(update, context, welcome_msg)
    

#Handler /help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_msg=textwrap.dedent('''
        🆘 <b>Do you need help?</b> 
        
        Here, a list for you:
        - /add | new deck

        <b>More doubts?</b>
        Contact us on Github: [link]
    ''')
    await show_keyboard(update, context, help_msg)

#Command for unknown or unsupported inputs
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    unknown_msg=textwrap.dedent("🤔 I don't understand. Please use the /help command to see what functionalities I support.")
    await update.message.reply_html(text=unknown_msg)
    await show_keyboard(update, context, unknown_msg)



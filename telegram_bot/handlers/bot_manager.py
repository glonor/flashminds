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
    
        welcome_msg = (
            f"🚀 Welcome to FlashMindsBot! 🧠\n\n"
            "Struggling with study sessions? Our bot is here to revolutionize your learning experience! "
            "Thanks to the power of Machine Learning and our innovative flashcard system, we generate flashcards "
            "from images and questions/answers provided by you.\n\n"
            "✨ How it works:\n"
            "1️⃣ Upload images or input your Q&A.\n"
            "2️⃣ ML generates personalized flashcards.\n"
            "3️⃣ Questions are paraphrased in each session.\n"
            "4️⃣ Evaluate your answers during the session.\n\n"
            "🔄 Smart Revision:\n"
            "Our algorithm identifies areas that need review and prioritizes them in subsequent sessions. "
            "Effortless learning tailored to your needs!\n\n"
            "📚 Unleash the potential of FlashMindsBot for a smarter study journey. Try it now and boost your academic success! 🌟\n\n"
        )        

    elif create_user_res.status_code == 409: #user already exist
        welcome_msg = textwrap.dedent(
            f'''
            🌟 Welcome back {user.mention_html()}! 🚀

            Ready to dive into another round of effective studying? 🧠✨ We're thrilled to have you back!
            '''
        )

    else: #error
        welcome_msg = f"Internal error. Status code: {create_user_res.status_code}"
    
    reply_markup = await show_keyboard(update, context)
    await update.message.reply_html(text=welcome_msg, reply_markup=reply_markup)
    
#Handler /help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
            f"🆘 Do you need help?\n\n"
            f"- /add : new deck\n"
            f"- /remove : remove deck\n"
            f"- /decks : list deck\n"
            f"- /study : start a session\n\n"
            f"More doubts? 🧐 Contact us on GitHub"

    )

    reply_markup = await show_keyboard(update, context)
    await update.message.reply_html(text=msg, reply_markup=reply_markup)

#Command for unknown or unsupported inputs
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    unknown_msg=textwrap.dedent("🤔 I don't understand. Please use the /help command to see what functionalities I support.")
    reply_markup = await show_keyboard(update, context)
    await update.message.reply_html(text=unknown_msg, reply_markup=reply_markup)



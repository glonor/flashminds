import textwrap
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests

#URL for the database
BL_API_BASE_URL = "http://localhost:5000"

#Handler /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram account data
    check_user_endpoint = f"{BL_API_BASE_URL}/check_user"
    create_user_endpoint = f"{BL_API_BASE_URL}/create_user"

    #Check if the user exists
    check_user_res = requests.get(check_user_endpoint, json={"user_id": user.id})
    welcome_msg=""

    if check_user_res.status_code == 404: #user not found
        #Create the user using the /create_user endpoint
        create_user_res = requests.post(create_user_endpoint, json={"user_id": int(user.id), "username": str(user.full_name)})

        if create_user_res.status_code == 201:  #creation done          
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
        else: #error
            welcome_msg += f"\nError creating user. Status code: {create_user_res.status_code}"

    elif check_user_res.status_code == 200: #user already exist
        welcome_msg = textwrap.dedent(
            f'''
            🌟 Welcome back {user.mention_html()}! 🚀

            Embark on another session of enhanced learning with FlashMinds. 🧠✨ We're thrilled to have you back!
            '''
        )

    else: #error
        welcome_msg = f"Internal error. Status code: {check_user_res.status_code}"

    await update.message.reply_html(text=welcome_msg)

#Handler /help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_msg=textwrap.dedent('''
        🆘 <b>Do you need help?</b> 
        
        Here, a list for you:
        - /add | new deck

        <b>More doubts?</b>
        Contact us on Github: [link]
    ''')
    await update.message.reply_html(text=help_msg)

#Command for unknown or unsupported inputs
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    unknown_msg=textwrap.dedent("I don't understand. Please use the `/help` command to see what functionalities I support.")
    await update.message.reply_html(text=unknown_msg)

import textwrap
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests

#URL for the database
DATABASE = "http://127.0.0.1:8000"

#Handler /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    res = requests.get(DATABASE + f"/users/{user.id}")

    #check if the user exists
    if res.status_code == 200:
        welcome_msg = textwrap.dedent(
        '''👋 Welcome back {}, good to see you again. Let's start studying together.''').format(user.mention_html())
        
    elif res.status_code == 206:
        welcome_msg = textwrap.dedent(
        '''👋 Hello {}, I am <b>FlashMindsBot</b>, I will be your support during the study sessions.''').format(user.mention_html())
        res = requests.post(DATABASE + f"/users", data={"user_id": user.id})

    else:
        welcome_msg = f"Internal error. Status code: {response.status_code}"

    await update.message.reply_html(text=welcome_msg)
    

#Handler /help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_msg=textwrap.dedent('''
        🆘 <b>Do you need help?</b> Here is a list of commands for you:

        ❓ <b>More doubts?</b>
        Contact us on Github: [link]
    ''')
    await update.message.reply_html(text=help_msg)

#Command for unknown or unsupported inputs
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    unknown_msg=textwrap.dedent("I don't understand. Please use the `/help` command to see what functionalities I support.")
    await update.message.reply_html(text=unknown_msg)

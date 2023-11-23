from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import ContextTypes
import requests, textwrap


CHOOSING, MENU, QUESTION, ANSWER = range(4)

decks = {}
BL_API_BASE_URL = "http://localhost:5000"

# ------------------ start HANDLER /ADD COMMAND ------------------ #
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 I'm ready! Let's create a new deck. What would you like to name it? \n\n /cancel")
    return CHOOSING

#1 ---- set deck 
async def set_deck_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_deck_endpoint = f"{BL_API_BASE_URL}/create_deck"

    user = update.effective_user  #telegram user
    deck_name = update.message.text  #input user
    msg = ""

    # Check if the deck exists
    create_deck_res = requests.post(create_deck_endpoint, json={"deck_name": str(deck_name), "user_id": int(user.id)}, timeout=10)

    if create_deck_res.status_code == 201:  #deck created
        msg = textwrap.dedent(
            f'''
            ✅ Well done! You have created a new deck called "<b>{deck_name}</b>"
            '''
        )
        await update.message.reply_html(text=msg)
        await update.message.reply_html("✍️ Now, write your first question card:")

        return QUESTION

    elif create_deck_res.status_code == 409:  #deck already exists
        msg = textwrap.dedent(
            f'''
            🙈 Oh! You have already created a new deck called "<b>{deck_name}</b>"
            Try another name.
            '''
        )
        await update.message.reply_html(text=msg)
        return CHOOSING  #repeat the name procedure

    else:  # error
        msg = f"Internal error. Status code: {create_deck_res.status_code}"
        await update.message.reply_html(text=msg)
    
    return CHOOSING 

#3 ---- write question 
async def write_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  #telegram user
    question = update.message.text #question text
    print(question)
    await update.message.reply_text("✍️ Write answer releted to the card:")

    return ANSWER

#4 ---- set answer
async def write_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  #telegram user
    answer = update.message.text #question text
    print(answer)

    keyboard = [
        [
            InlineKeyboardButton("➕ Question Card", callback_data='add_question'),
            InlineKeyboardButton("Cancel", callback_data='finish')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👇 Choose an option:", reply_markup=reply_markup)
    return QUESTION

# ------------------ end HANDLER /ADD COMMAND ------------------ #

# ------------------ start HANDLER button ------------------ #

#1 ---- button handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == 'add_question': #user click on "new question"
        await query.edit_message_text("Write another question card:")

    elif query.data == 'finish': #user click on "done"
        await query.edit_message_text("✅ Creation done, Thank you!")       
        return ConversationHandler.END

#2 ---- cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in decks:
        del decks[user_id]
        await update.message.reply_text("Hai annullato la creazione del deck.")
    else:
        await update.message.replytext("Comando annullato.")

    print("cioa")
    return ConversationHandler.END

# ------------------ end HANDLER button ------------------ #



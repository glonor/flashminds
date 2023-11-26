from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import ContextTypes
import requests, textwrap

DECK, QUESTION, ANSWER, ADD_ANOTHER = range(4)
escape = False
decks = {}
BL_API_BASE_URL = "http://localhost:5000"

# ---------------------------------------------------------------- #
# ------------------ start HANDLER /ADD COMMAND ------------------ #
# ---------------------------------------------------------------- #

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 I'm ready! Let's create a new deck. What would you like to name it? \n\n /cancel")
    return DECK

#1 ---- set deck 
async def set_deck_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_deck_endpoint = f"{BL_API_BASE_URL}/create_deck"

    user = update.effective_user #telegram user
    deck_name = update.message.text #input user
    msg = ""

    #Check if the deck exists
    create_deck_res = requests.post(create_deck_endpoint, json={"deck_name": str(deck_name), "user_id": int(user.id)}, timeout=10)

    if create_deck_res.status_code == 201:  #deck created
        response_data = create_deck_res.json()
        deck_id = response_data.get('deck_id', None)
        context.user_data['deck_id'] = deck_id

        msg = textwrap.dedent(
            f'''
            ✅ Well done! You have created a new deck called "<b>{deck_name}</b>"
            '''
        )
        await update.message.reply_html(text=msg)
        await update.message.reply_html("1️⃣ Now, write your first card's question")

        return QUESTION

    elif create_deck_res.status_code == 409:  #deck already exists
        msg = textwrap.dedent(
            f'''
            🙈 Oh! You have already created a new deck called "<b>{deck_name}</b>"
            Try another name.
            '''
        )
        await update.message.reply_html(text=msg)
        return DECK  #repeat naming procedure

    else:  #error
        msg = f"Internal error. Status code: {create_deck_res.status_code}"
        await update.message.reply_html(text=msg)
    
    return DECK 

#2 ---- question 
async def set_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  #telegram user
    question = update.message.text #question text
    
    context.user_data['question'] = question

    await update.message.reply_text("2️⃣ Write card's answer")
    return ANSWER

#3 ---- answer
async def set_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_card_endpoint = f"{BL_API_BASE_URL}/add_flashcard"
    user = update.effective_user #telegram user
    answer = update.message.text #question text

    #Create card
    create_card_res = requests.post(create_card_endpoint, json={"question": str(context.user_data['question']), "answer": str(answer), "user_id": int(user.id), "deck_id": int(context.user_data['deck_id'])}, timeout=10)

    if create_card_res.status_code != 201:  #error
        msg = f"Internal error. Status code: {create_card_res.status_code}"
        await update.message.reply_html(text=msg)
        await update.message.reply_text("Sorry, rewrite your question:")
        return QUESTION


    keyboard = [
        [InlineKeyboardButton("➕ Card", callback_data='yes')],
        [InlineKeyboardButton("✋ End", callback_data='no')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👇 Choose an option", reply_markup=reply_markup)

    return ADD_ANOTHER

#4 ---- add another question
async def add_another(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_answer = query.data
    if user_answer == 'yes':
        await update.callback_query.message.edit_text("1️⃣ Write next card:")
        return QUESTION
        
    else:
        result_message="🥳 A deck has been created. Use the /study to start a session."
        await update.callback_query.message.edit_text(result_message)
        context.user_data.clear()
        return ConversationHandler.END #loop exit

#5 ---- cancel 
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    await update.message.reply_text("🛑 You cancelled the deck creation.")
    context.user_data.clear()
    return ConversationHandler.END

# ---------------------------------------------------------------- #
# ------------------  end HANDLER /ADD COMMAND  ------------------ #
# ---------------------------------------------------------------- #

# ---------------------------------------------------------------- #
# ------------------ start HANDLER /REMOVE COMMAND --------------- #
# ---------------------------------------------------------------- #

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_decks_endpoint = f"{BL_API_BASE_URL}/get_decks"
    user = update.effective_user #telegram user
    deck_name = update.message.text #input user

    #user deck list
    get_decks_res = requests.get(get_decks_endpoint, json={"user_id": int(user.id)}, timeout=10)

    if get_decks_res.status_code == 200:  #list deck ok
        response_data = get_decks_res.json()
        decks = response_data.get('decks', [])

        if not decks: #empty list
            await update.message.reply_html(text="👀 No decks are present. You can create one with the command /add ")

        else:
            keyboard=[]

            for deck in decks:
                deck_id = deck.get('deck_id')
                deck_name = deck.get('deck_name')
                button = InlineKeyboardButton(deck_name, callback_data=f"remove_deck_{deck_id}")
                keyboard.append([button])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🗑️ Choose the deck you want to remove", reply_markup=reply_markup)

    else:  #error
        msg = f"Internal error. Status code: {create_deck_res.status_code}"
        await update.message.reply_html(text=msg)

#1 ---- remove specific deck
async def remove_deck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remove_deck_endpoint = f"{BL_API_BASE_URL}/remove_deck"

    query = update.callback_query
    user_answer = query.data
    user_id = update.effective_user.id
    deck_id = int(query.data.split("_")[2])  #ID extraction

    remove_deck_res = requests.delete(remove_deck_endpoint, json={"deck_id": deck_id}, timeout=10)

    if remove_deck_res.status_code == 200: #success
        await update.callback_query.message.edit_text("🚮 Deck deleted successfully")
    
    else:
        await update.callback_query.message.edit_text(f"Internal error. Status code: {remove_deck_res.status_code}")
        

# ---------------------------------------------------------------- #
# ------------------  end HANDLER /ADD COMMAND  ------------------ #
# ---------------------------------------------------------------- #

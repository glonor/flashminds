from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import ContextTypes
import requests, textwrap
import os 
from io import BytesIO

from handlers.bot_manager import *


DECK, INPUT, IMAGE, REGENERATE, QUESTION, ANSWER = range(6)

BL_API_BASE_URL = "http://localhost:5000"
GPT_API_BASE_URL = "http://localhost:5002"
OCR_API_BASE_URL = "http://localhost:5003"

# ---------------------------------------------------------------- #
# ------------------ start HANDLER /ADD COMMAND ------------------ #
# ---------------------------------------------------------------- #

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 I'm ready! Let's create a new Deck. What would you like to name it? \n\n /cancel", reply_markup=ReplyKeyboardRemove())
    return DECK

#1 ---- set deck name
async def set_deck_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    deck_name = update.message.text #input user

    create_deck_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks"
    msg = ""

    create_deck_res = requests.post(create_deck_endpoint, json={"deck_name": str(deck_name)}, timeout=10)

    if create_deck_res.status_code == 201:  #deck created
        response_data = create_deck_res.json()
        deck_id = response_data.get('deck_id', None)
        context.user_data['deck_id'] = deck_id

        keyboard = [
            [InlineKeyboardButton("Write manually ✍️", callback_data='text')],
            [InlineKeyboardButton("Generate from image ✨", callback_data='pic')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("How would you like to create a flashcard?", reply_markup=reply_markup)

        return INPUT

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

#2 ---- choose type input: text or image
async def opt_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_answer = query.data
    if user_answer == 'text':
        msg = (
            "Great choice! 🌟 You've selected to enter the question and answer as text.\n\n"
            "Please reply with your question, and I'll guide you through the next steps.\n\n"
        )
        await update.callback_query.message.edit_text(msg)
        return QUESTION
        
    elif user_answer == 'pic':
        msg=(
            "Do you like magic? 🎩 Please send the image or slide you'd like to turn into a flashcard.\n\n"
            "⚠️ PDF files are not supported. Please make sure to send only one image (PNG, JPEG, JPG) or a picture in your message."
        )
        
        await update.callback_query.message.edit_text(msg)
        return IMAGE
    else:
        result_message="FAN-TAS-TIC 🥳 \nA deck has been created. Use the /study to start a session."
        await update.callback_query.message.edit_text(result_message)
        context.user_data.clear()
        return ConversationHandler.END #loop exit

#3a ---- generate card: OCR + GPT
async def get_card_generated(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  # Telegram user
    message = update.message

    if not message.photo:
        await update.message.reply_text("Oh nooo!😮 The uploaded file is not a photo \nRetry.")
        return IMAGE

    file_id = message.photo[-1].file_id
    chat_id = update.message.chat_id


    #Download the image
    file = await context.bot.get_file(file_id)
    file_path = os.path.expanduser('~') + '/' + file_id + ".jpg"
    await file.download_to_drive(file_path)


    # Send the photo to the OCR API using a POST request
    perform_ocr_endpoint = f"{OCR_API_BASE_URL}/perform_ocr"
    with open(file_path, "rb") as file:
        perform_ocr_res = requests.post(perform_ocr_endpoint, files={"image": file})
    
    await update.message.reply_text("Let the magic begin!✨🔮")
    # Process the OCR API response if needed
    if perform_ocr_res.status_code == 200:
        response_data = perform_ocr_res.json()
        text = response_data.get('text',"")
        print(text)
        context.user_data['text_ocr'] = text


        gpt_generate_endpoint = f"{GPT_API_BASE_URL}/generate_flashcard"
        gpt_generate_res = requests.post(gpt_generate_endpoint, json={"text": text})

        if gpt_generate_res.status_code == 200:
            response_data = gpt_generate_res.json()
            
            generated_question = response_data.get('question',"")
            context.user_data['generated_question'] = generated_question
            
            generated_answer = response_data.get('answer',"")
            context.user_data['generated_answer'] = generated_answer
            
            keyboard = [
                [InlineKeyboardButton("OK", callback_data='ok')],
                [InlineKeyboardButton("♻️ Regenerate", callback_data='regenerate')]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            
            msg = (
                    f"👏 Fantastic! Your flashcard has been created:\n\n"
                    f"- Question:\n{generated_question}\n\n"
                    f"- Answer:\n {generated_answer}\n\n"
                    "Feel free to ask for another flashcard or press OK to complete the magic! ✨🔮"
            )
            await update.message.reply_text(text=msg, reply_markup=reply_markup)
            return REGENERATE

        else:
            msg = f"Internal error. Status code: {gpt_generate_res.status_code}"
            await update.message.reply_html(text=msg)

            return IMAGE

    else:
        msg = f"Internal error. Status code: {perform_ocr_res.status_code}"
        await update.message.reply_html(text=msg)

    #clean up the downloaded file
    os.remove(file_path)

#3a ---- regenerate card: OCR + GPT
async def regenerate_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    query = update.callback_query
    user_answer = query.data
    if user_answer == 'regenerate':
        
        gpt_generate_endpoint = f"{GPT_API_BASE_URL}/generate_flashcard"
        gpt_generate_res = requests.post(gpt_generate_endpoint, json={"text": context.user_data['text_ocr']})

        if gpt_generate_res.status_code == 200:
            response_data = gpt_generate_res.json()
            generated_question = response_data.get('question',"")
            generated_answer = response_data.get('answer',"")
            
            context.user_data['generated_question']=generated_question
            context.user_data['ansgenerated_answerwer']=generated_answer

            msg = (
                    f"♻️ Regenerated! Your flashcard has been created:\n\n"
                    f"- Question:\n{generated_question}\n\n"
                    f"- Answer:\n {generated_answer}\n\n"
                    "Feel free to ask for another flashcard or press OK to complete the magic! ✨🔮"
            )

            keyboard = [
                [InlineKeyboardButton("OK", callback_data='ok')],
                [InlineKeyboardButton("♻️ Regenerate", callback_data='regenerate')]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=msg, reply_markup=reply_markup)
            return REGENERATE
            
    elif user_answer == 'ok':
        create_card_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks/{context.user_data['deck_id']}/flashcards"

        #Create card
        create_card_res = requests.post(create_card_endpoint, json={"question": str(context.user_data['generated_question']), "answer": str(context.user_data['generated_answer'])}, timeout=10)

        if create_card_res.status_code != 201:  #error
            msg = f"Internal error. Status code: {create_card_res.status_code}"
            await update.message.reply_html(text=msg)
            await update.message.reply_text("Sorry, rewrite your card 🤧")

        keyboard = [
            [InlineKeyboardButton("Write manually ✍️", callback_data='text')],
            [InlineKeyboardButton("Generate from image ✨", callback_data='pic')],
            [InlineKeyboardButton("Finish", callback_data='finish')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Thank you. What would you like to do next?", reply_markup=reply_markup)        
        return INPUT

#3b ---- question 
async def set_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  #telegram user
    question = update.message.text #question text
    
    context.user_data['question'] = question

    await update.message.reply_text("Awesome! Now, please reply with the answer to complete the process. ✨")
    return ANSWER

#3b ---- answer
async def set_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    answer = update.message.text #question text

    create_card_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks/{context.user_data['deck_id']}/flashcards"

    #Create card
    create_card_res = requests.post(create_card_endpoint, json={"question": str(context.user_data['question']), "answer": str(answer)}, timeout=10)

    if create_card_res.status_code != 201:  #error
        msg = f"Internal error. Status code: {create_card_res.status_code}"
        await update.message.reply_html(text=msg)
        await update.message.reply_text("Sorry, rewrite your question 🤧")
        return QUESTION

    keyboard = [
        [InlineKeyboardButton("Write manually ✍️", callback_data='text')],
        [InlineKeyboardButton("Generate from image ✨", callback_data='pic')],
        [InlineKeyboardButton("Finish", callback_data='finish')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Thank you. What would you like to do next?", reply_markup=reply_markup)
    return INPUT
     
#4 ---- cancel 
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    msg="🛑 You cancelled the deck creation."
    context.user_data.clear()
    reply_markup = await show_keyboard(update, context)
    await update.message.reply_text(msg, reply_markup=reply_markup)
    return ConversationHandler.END

# ---------------------------------------------------------------- #
# ------------------ start HANDLER /REMOVE COMMAND --------------- #
# ---------------------------------------------------------------- #

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

                button = InlineKeyboardButton(f"{deck_name} - Cards: {flashcard_count}", callback_data=f"remove_deck_{deck_id}")
                keyboard.append([button])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🗑️ Choose the deck you want to remove", reply_markup=reply_markup)
            

    else:  #error
        msg = f"Internal error. Status code: {get_decks_res.status_code}"
        await update.message.reply_html(text=msg)

#1 ---- remove specific deck
async def remove_deck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_answer = query.data
    user = update.effective_user
    deck_id = int(query.data.split("_")[2])  #ID extraction

    remove_deck_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks/{deck_id}"
    remove_deck_res = requests.delete(remove_deck_endpoint, timeout=10)

    if remove_deck_res.status_code == 200: #success
        await update.callback_query.message.edit_text("🚮 Deck deleted successfully")
    
    else:
        await update.callback_query.message.edit_text(f"Internal error. Status code: {remove_deck_res.status_code}")
        
# ---------------------------------------------------------------- #
# ------------------  start HANDLER /DECKS COMMAND  -------------- #
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
                msg += f"\n ➡️ <b>{deck_name}</b> - Cards: {flashcard_count}"

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
    menu = ReplyKeyboardMarkup(keyboard, resize_keyboard= True, one_time_keyboard=True)
    return menu

#menu action call
async def reply_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    #action allowed
    actions = {
        "✨ Start a session ✨": decks(update, context),
        "📚 Decks": decks(update, context),
        "✚ New Deck": add(update, context),
        "🗑️ Remove": remove(update, context),
        "/cancel": cancel(update, context)
    }

    action_function = actions.get(text)
    if action_function:
        await action_function

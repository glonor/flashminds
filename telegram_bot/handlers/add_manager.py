from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.ext import ContextTypes
import requests, textwrap
import os 
from io import BytesIO

from handlers.bot_manager import *

BL_API_BASE_URL = os.environ.get('DL_URL')
SC_API_BASE_URL = os.environ.get('SCHEDULER_URL')
GPT_API_BASE_URL = os.environ.get('CHATGPT_URL')
OCR_API_BASE_URL = os.environ.get('OCR_URL')



NAME, OPTION, QUESTION, ANSWER, IMAGE, REGENERATE = range(6) #state - conversation_handler_add

# ---------------------------------------------------------------- #
# ----------------------  HANDLER /ADD COMMAND ------------------- #
# ---------------------------------------------------------------- #

#1 ---- Deck Name
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 I'm ready! Let's create a new Deck. What would you like to name it? \n\n /cancel", reply_markup=ReplyKeyboardRemove())
    return NAME

#2 ---- Deck Name Control
async def study_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    deck_name = update.message.text #input user

    create_deck_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks" #endpoint deck
    create_deck_res = requests.post(
        create_deck_endpoint, 
        json={
            "deck_name": str(deck_name)
        })
    
    if create_deck_res.status_code == 201:  #deck created
        response_data = create_deck_res.json()
        deck_id = response_data.get('deck_id', None)
        
        context.user_data['deck_id'] = deck_id #save deck_id

        keyboard = [
            [KeyboardButton("Write manually ✍️")],
            [KeyboardButton("Generate from image ✨")]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
        await update.message.reply_text("How would you like to create a flashcard?", reply_markup=reply_markup)

    elif create_deck_res.status_code == 409:  #deck already exists
        msg = textwrap.dedent(
            f'''
            🙈 Oooh! You have already created a deck called "<b>{deck_name}</b>"
            Try another name.
            '''
        )
        await update.message.reply_html(text=msg)
        return NAME  #repeat naming procedure

    else:  #error        
        reply_markup = await show_keyboard(update, context)
        msg = f"Internal error. Status code: {create_deck_res.status_code}"
        await update.message.reply_html(text=msg, reply_markup=reply_markup)
        context.user_data.clear()
        return ConversationHandler.END #exit
    
    return OPTION 

#2 ---- Deck Input Type Selection
async def study_input_opt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    option = update.message.text #input user

    #manage user reply
    if option == "Write manually ✍️": 
        msg = (
            "Great choice! 🌟 You've selected to enter the question and answer as text.\n\n"
            "Please reply writing your question, and I'll guide you through the next steps.\n\n"
        )
        await update.message.reply_text(msg)
        return QUESTION

    elif option == "Generate from image ✨":
        msg=(
            "Do you like magic? 🎩 Please send the image or slide you'd like to turn into a flashcard.\n\n"
            "⚠️ PDF files are not supported. Please make sure to send only one image (PNG, JPEG, JPG) or a picture in your message."
        )
        await update.message.reply_text(msg)
        return IMAGE

    elif option == "Finish 🏁":
        reply_markup = await show_keyboard(update, context)
        msg="FAN-TAS-TIC 🥳 \nA deck has been created. Use the /study to start a session."
        await update.message.reply_text(msg, reply_markup=reply_markup)
        context.user_data.clear()
        return ConversationHandler.END #loop exit

    else: #option not valid, repeat
        keyboard = [
            [KeyboardButton("Write manually ✍️")], 
            [KeyboardButton("Generate from image ✨")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
        await update.message.reply_text(f"Repeat the choice.", reply_markup=reply_markup)
        return OPTION

#3a ---- Deck Input Manually | Set question
async def study_set_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    question = update.message.text #input user

    context.user_data['question'] = question

    await update.message.reply_text("Awesome! Now, please reply with the answer to complete the process. ✨")
    return ANSWER

#3a ---- Deck Input Manually | Set answer
async def study_set_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    answer = update.message.text #question text

    create_card_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks/{context.user_data['deck_id']}/flashcards" #endpoint flashcard

    #Create card
    create_card_res = requests.post(
        create_card_endpoint, 
        json={
            "question": str(context.user_data['question']), 
            "answer": str(answer)
        })

    if create_card_res.status_code != 201:  #error
        reply_markup = await show_keyboard(update, context)
        msg = f"Internal error. Status code: {create_card_res.status_code}"
        await update.message.reply_html(text=msg, reply_markup=reply_markup)
        context.user_data.clear()
        return ConversationHandler.END #exit

    keyboard = [
        [KeyboardButton("Write manually ✍️")],
        [KeyboardButton("Generate from image ✨")],
        [KeyboardButton("Finish 🏁")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
    await update.message.reply_text("Thank you. What would you like to do next?", reply_markup=reply_markup)
    return OPTION

#3b ---- Deck Input From Image
async def study_set_card_from_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  # Telegram user
    message = update.message

    if not message.photo: #ensure that input is an image
        await update.message.reply_text("The uploaded file is not a photo \nRetry to upload.")
        return IMAGE

    await update.message.reply_text("Let the magic begin!✨🔮")

    #Download the image
    file_id = message.photo[-1].file_id
    chat_id = update.message.chat_id
    file = await context.bot.get_file(file_id)
    file_path = os.path.expanduser('~') + '/' + file_id + ".jpg"
    await file.download_to_drive(file_path)

    #Send the photo to the OCR API using a POST request
    perform_ocr_endpoint = f"{OCR_API_BASE_URL}/perform_ocr" #ocr endpoint
    with open(file_path, "rb") as file:
        perform_ocr_res = requests.post(
            perform_ocr_endpoint, 
            files={
                "image": file
            }
        )
    
    if perform_ocr_res.status_code == 200: #ocr success
        response_data = perform_ocr_res.json()
        text = response_data.get('text',"")
        
        context.user_data['text_ocr'] = text #save text_ocr

        gpt_generate_endpoint = f"{GPT_API_BASE_URL}/generate_flashcard" #endpoint chatgpt
        gpt_generate_res = requests.post(
            gpt_generate_endpoint, 
            json={
                "text": text
            }
        )

        if gpt_generate_res.status_code == 200: #chatgpt success
            response_data = gpt_generate_res.json()
            
            generated_question = response_data.get('question',"")
            context.user_data['generated_question'] = generated_question #save generated_question
            
            generated_answer = response_data.get('answer',"")
            context.user_data['generated_answer'] = generated_answer #save generated_answer
            
            keyboard = [
                [KeyboardButton("OK")],
                [KeyboardButton("♻️ Regenerate")]
            ]

            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
            
            msg = (
                    f"👏 Fantastic! Your flashcard has been created:\n\n"
                    f"- Question:\n{generated_question}\n\n"
                    f"- Answer:\n {generated_answer}\n\n"
                    "Feel free to regenerate the flashcard or press OK to complete the magic! ✨🔮"
            )
            await update.message.reply_text(text=msg, reply_markup=reply_markup)

        else: #error chatgpt
            msg = f"Internal error. Status code: {gpt_generate_res.status_code}. Retry to upload the image."
            await update.message.reply_html(text=msg)
            return IMAGE

    else: #error ocr
        msg = f"Internal error. Status code: {perform_ocr_res.status_code}.  Retry to upload the image."
        await update.message.reply_html(text=msg)
        return IMAGE

    #clean up the downloaded file
    os.remove(file_path)

    return REGENERATE

#3b ---- Deck Input From Image | Regeneration
async def study_regenerate_card_from_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user #telegram user
    option = update.message.text #input user

    #manage user reply
    if option == "OK": 
        create_card_endpoint = f"{BL_API_BASE_URL}/users/{user.id}/decks/{context.user_data['deck_id']}/flashcards" #endpoint flashcard

        #card creation
        create_card_res = requests.post(
            create_card_endpoint, 
            json={
                "question": str(context.user_data['generated_question']), 
                "answer": str(context.user_data['generated_answer'])
            }
        )

        if create_card_res.status_code != 201:  #error
            reply_markup = await show_keyboard(update, context)
            msg = f"Internal error. Status code: {create_card_res.status_code}"
            await update.message.reply_html(text=msg, reply_markup=reply_markup)
            context.user_data.clear()
            return ConversationHandler.END #exit

        keyboard = [
            [KeyboardButton("Write manually ✍️")],
            [KeyboardButton("Generate from image ✨")],
            [KeyboardButton("Finish 🏁")]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard= True, one_time_keyboard=True)
        await update.message.reply_text(text="Thank you. What would you like to do next?", reply_markup=reply_markup)        
        return OPTION

    elif option == "♻️ Regenerate":
        gpt_generate_endpoint = f"{GPT_API_BASE_URL}/generate_flashcard" #chatgpt endpoint
        gpt_generate_res = requests.post(
            gpt_generate_endpoint, 
            json={
                "text": context.user_data['text_ocr']
                }
        )

        if gpt_generate_res.status_code == 200: #chatgpt success
            response_data = gpt_generate_res.json()
            generated_question = response_data.get('question',"")
            generated_answer = response_data.get('answer',"")
            
            context.user_data['generated_question']=generated_question #save generated_question
            context.user_data['ansgenerated_answerwer']=generated_answer #save generated_asnwer

            msg = (
                    f"♻️ Regenerated! Your flashcard has been created:\n\n"
                    f"- Question:\n{generated_question}\n\n"
                    f"- Answer:\n {generated_answer}\n\n"
                    "Feel free to regenerate the flashcard or press OK to complete the magic! ✨🔮"
            )

            keyboard = [
                [KeyboardButton("OK")],
                [KeyboardButton("♻️ Regenerate")]
            ]

            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
            await update.message.reply_text(text=msg, reply_markup=reply_markup)
            return REGENERATE

    else: #option not valid, repeat
        keyboard = [
            [KeyboardButton("OK")], 
            [KeyboardButton("♻️ Regenerate")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard= True)
        await update.message.reply_text(f"Repeat the choice.", reply_markup=reply_markup)
        return REGENERATE

#4 ---- Fallback (Cancel)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    msg="🛑 You cancelled the deck creation."
    context.user_data.clear()
    reply_markup = await show_keyboard(update, context)
    await update.message.reply_text(msg, reply_markup=reply_markup)
    return ConversationHandler.END

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
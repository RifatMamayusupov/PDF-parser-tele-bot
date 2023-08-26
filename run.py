from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, CallbackContext, Updater, MessageHandler, filters,ApplicationBuilder,CallbackQueryHandler
from PyPDF2 import PdfReader
from tqdm import tqdm
import requests
import os

def extract_text_pdf_kril(path, russian_folder):
    print('Data yigish boshlandi.....\n')
    reader = PdfReader(path)

    for page in tqdm(reader.pages):
        text = page.extract_text()

        if any(char in text for char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
            with open(russian_folder, 'a', encoding='utf-8') as f_russian:
                f_russian.write(text)

    print('\n\nData yigish tugadi.....')

def extract_text_pdf_lotin(path, uzbek_folder):
    print('Data yigish boshlandi.....\n')
    reader = PdfReader(path)

    for page in tqdm(reader.pages):
        text = page.extract_text()

        if any(char in text for char in "abcdefghijklmnopqrstuvwxyz"):
            with open(uzbek_folder, 'a', encoding='utf-8') as f_uzbek:
                f_uzbek.write(text)

    print('\n\nData yigish tugadi.....')

file_folder_kril='custom_kril/'
file_folder_lotin='custom_lotin/'


async def start(update: Update, context: CallbackContext):
      global start_keyboard
      start_keyboard = [
          [
               
           InlineKeyboardButton(text="Kril-text🇷🇺", callback_data='kril'),
           InlineKeyboardButton(text="Lotin-text🇺🇿", callback_data='lotin'),

         ]
      ]

      text = "<b><i> Assalomu alaykum !\n\n PDF parser botiga xush kelibsiz.\n\n.File - qaysi alfabetda ekanligiga etibor berib,\n\nkerakli tilni tanlang !📝</i></b>"
      try:
            await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(start_keyboard))

      except Exception as e:
        return f"Message failed: {e}"

async def button_callback(update: Update, context: CallbackContext):
    global query

    query = update.callback_query
    await query.answer()
    
    if query.data == 'kril':
        context.user_data['step']="kril"

        await query.edit_message_text( text=f"<b><i> Siz {query.data} alfabetini tanladingiz, Kril tildagi .PDF file yuboring !</i></b>", parse_mode=ParseMode.HTML)
    
    elif query.data == 'lotin':
           context.user_data['step']="lotin"
          
           await query.edit_message_text(text=f"<b><i>Siz {query.data} alfabetni tanladingiz, Lotin tildagi .PDF file yuboring !</i></b>", parse_mode=ParseMode.HTML)
    elif query.data not in ['kril', 'lotin']:
          
             await context.bot.send_message(chat_id=update.effective_chat.id, text= "<b><i>Siz ya'na MAIN sectionda😃</i></b>", reply_markup=InlineKeyboardMarkup(start_keyboard), parse_mode=ParseMode.HTML) 

async def extract_text(update: Update, context: CallbackContext):
      
      text = "<b><i>.pdf file yuborganiz uchun rahmat !\n\nFile muaffaqiyatli saqlandi.</i></b>"

      if context.user_data['step']=="kril":

            document = update.message.document
            file = await context.bot.get_file(document.file_id)

            filename = requests.get(file.file_path) 
            file_path = os.path.join(file_folder_kril, os.path.basename(file.file_path))
            with open(file_path, "wb") as f:
                  f.write(filename.content)

            keyboard = [
                           [
                              InlineKeyboardButton(text="🔄Main", callback_data="back"),
                        ]
                  ]      
            
            await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
            
            extract_text_pdf_kril(file_path, "data-hub/dataset_kril.txt")

      elif context.user_data['step']=="lotin":

            document = update.message.document
            file = await context.bot.get_file(document.file_id)

            filename = requests.get(file.file_path) 
            file_path = os.path.join(file_folder_lotin, os.path.basename(file.file_path))
            with open(file_path, "wb") as f:
                  f.write(filename.content)
            
            keyboard = [
                           [
                              InlineKeyboardButton(text="🔄Main", callback_data="back"),
                              ]
                        ]  
            await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

            extract_text_pdf_lotin(file_path, "data-hub/dataset_lotin.txt")
           
application = ApplicationBuilder().token('6368516221:AAGd4fuOgiVA_wa1I9eaKbVxxE0XabIdPLY').build()

start_handler = CommandHandler('start', start)
application.add_handler(start_handler)

parser_handler = MessageHandler(filters.ATTACHMENT, extract_text)
application.add_handler(parser_handler)

application.add_handler(CallbackQueryHandler(button_callback))

print('Bot ishga tushdi ...')
application.run_polling()

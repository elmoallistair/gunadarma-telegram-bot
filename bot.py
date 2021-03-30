from telegram import ParseMode
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, Filters
import button
import configparser as cfg
import logging
import response

def read_token(config_file):
    parser = cfg.ConfigParser()
    parser.read(config_file)
    return parser.get("creds", "token")

def error(update, context):
    logger.warning("Update '%s' caused error '%s'", update.update_id, context.error)

def reply(update, context):
    chat_id = update.message.chat.id
    message = update.message.text.lower()
    command = response.validate_message(message) 

    if command:
        response.create_reply(update, context, command)
    else:
        update.message.reply_text("Perintah tidak dikenali.")

def callback_query_handler(update, context):
    callback_query = update.callback_query
    callback_name = callback_query.data
    
    text = response.template_from_file(callback_name, from_callback=True)
    keyboard = button.create_button_from_callback(callback_name)
    callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

def main():
    token = read_token("config.cfg")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text, reply))
    dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))
    dispatcher.add_error_handler(error)

    updater.start_polling()
    print("Bot enabled... press CTRL+C to disabled")
    updater.idle()

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    main()
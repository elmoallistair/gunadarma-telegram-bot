from telegram import ParseMode
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, Filters
import button
import configparser as cfg
import datetime
import logging
import response
import scraping
import os

def read_token(config_file):
    """Read token from config file"""
    parser = cfg.ConfigParser()
    parser.read(config_file)
    return parser.get("creds", "token")

def error(update, context):
    """Log Errors caused by Updates"""
    logger.warning("Update '%s' caused error '%s'", update, context.error)

def reply(update, context):
    """Reply the user message"""
    message = update.message.text.lower()
    command = response.validate_message(message) 

    if command:
        response.reply_message(update, context, command)
    else:
        update.message.reply_text("Perintah tidak dikenali.")
    
def callback_query_handler(update, context):
    """Handle callback query"""
    callback_query = update.callback_query
    callback_name = callback_query.data
    callback_reply = response.get_template(f"callback/{callback_name}.html")
    keyboard = button.create_button_from_callback(callback_name)

    if callback_name == "jadwal_callback":
        callback_query.message.edit_caption(caption=callback_reply, parse_mode=ParseMode.HTML)
    else:
        callback_query.edit_message_text(text=callback_reply, reply_markup=keyboard, parse_mode=ParseMode.HTML)

def update_data(context):
    """Start scraping for update file"""
    scraping.start_scraping()

def main():
    """Start the bot"""
    # token = read_token("config.cfg")
    token = os.environ.get("TOKEN")
    updater = Updater(token)
    
    # Dispatcher for register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text, reply))
    dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))
    dispatcher.add_error_handler(error)

    # Update data daily
    job = updater.job_queue
    job.run_daily(update_data, time=datetime.time(hour=00, minute=00, second=00))
    
    # Start bot
    updater.start_polling()
    print("Bot enabled... press CTRL+C to disabled")
    # Run until the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    main()

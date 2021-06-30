from collections import OrderedDict
from datetime import datetime as dt
from operator import getitem
from pathlib import Path
from telegram import ParseMode
from textwrap import dedent
import scraping
import button
import yaml
import re

def validate_message(message):
    """Check if message contains valid command"""
    list_of_commands = ["/start", "/help", "/kalendar", "/berita", "/jadwal", 
                        "/jam", "/cuti", "/non_aktif", "/cek_nilai", 
                        "/pindah_kelas", "/pindah_jurusan", "/loker"]
    
    for word in message.split():
        if word in list_of_commands:
            return word[1:]
    return None


def load_data(command):
    """Load data from yaml file"""
    yaml_path = f"scrape_files/data/{command}.yaml"
    data = yaml.load(open(yaml_path), Loader=yaml.FullLoader)
    return data

def sort_data(data):
    """Sort data in dict by date in descending order"""
    key = lambda x: dt.strptime(getitem(x[1], "date"), "%d/%m/%Y")
    sorted_data = OrderedDict(sorted(data.items(), key=key, reverse=True))
    return sorted_data

def get_template(path):
    """Get reply template from html file"""
    file_path = f"response_templates/{path}"
    template=Path(file_path).read_text()
    return template

def send_image(context, chat_id, image_path, keyboard=None, caption=None):
    """Send image to user"""
    image = open(image_path, "rb")
    context.bot.sendPhoto(chat_id=chat_id, 
                          photo=image, 
                          reply_markup=keyboard, 
                          caption=caption, 
                          parse_mode=ParseMode.HTML)

def send_text(update, text, keyboard=None):
    """Send text to user"""
    update.message.reply_text(text=dedent(text), 
                              reply_markup=keyboard, 
                              parse_mode=ParseMode.HTML, 
                              disable_web_page_preview=True)

def reply_message(update, context, command):
    """Creating reply to user"""
    chat_id = update.message.chat.id

    # Get response text template
    try:
        text = get_template(f"command/{command}.html")
    except:
        text = None

    # Create button based on command
    try:
        keyboard = button.create_button(command)
    except:
        keyboard = None

    # Create and send reply for specific command
    if command == "kalendar":
        caption, image_path, _ = load_data(command).values()
        send_image(context, chat_id, image_path, keyboard, f"🗓 {caption}")
    elif command == "jam":
        image_path = load_data(command)["img_path"]
        send_image(context, chat_id, image_path)
    elif command == "loker":
        data = load_data(command)
        content = ""
        sorted_data = sort_data(data)
        for id in sorted_data:
            date, title, url = sorted_data[id].values()
            content += f"🗞 <b>({date})  <a href='{url}'>{title}</a></b>\n"
        text = text.format(content)
    elif command == "jadwal":
        keyboard = None
        message = update.message.text.lower() 
        try:
            message_split = message.split(" ", 1) # Split command and query
            cmd, query = message_split
            assert cmd == "/jadwal" # Must be in '/jadwal [KELAS_ATAU_DOSEN]' format
            try:
                assert len(query) >= 5 # Query must be 5 characters long
                # Scraping data
                try:
                    send_text(update, f"Mencari jadwal untuk input: <b>{query}</b> ...")
                    data = scraping.scraping_jadwal_kuliah(query)
                    if data: # Successful scraping
                        img_path, caption = data
                        keyboard = button.create_button(command)
                        send_image(context, chat_id, img_path, keyboard, dedent(caption))
                    else: # Query not found
                        text = get_template("error/jadwal_not_found.html").format(query)
                except Exception as err: # Failed scraping data
                    text = get_template("error/jadwal_failed_scraping.html").format(err)
            except: # Query length < 5
                text = get_template("error/jadwal_short_query.html")
        except: # Wrong format
            text = get_template("error/jadwal_wrong_format.html")
    elif command == "berita":
        data = load_data(command)
        message = update.message.text.lower()
        try:
            # Send news content by id
            message_split = message.split(" ", 1) # Split command and query
            cmd, query = message_split
            if cmd == "/berita": # Must be in '/berita [ID]' format 
                try:
                    content, _, title, _ = data[query].values()
                    text = f"<b>{title.upper()}</b>\n\n{content}"
                except: # ID not found
                    keyboard = None
                    text = get_template("error/berita_not_found.html").format(query)
            else: # Wrong format
                keyboard = None
                text = get_template("error/berita_wrong_format.html")
        except:
            # Send list of news
            content = ""
            sorted_data = sort_data(data)
            for id in sorted_data:
                _, date, title, url = sorted_data[id].values()
                content += f"🗞 <b>({date} - {id})  <a href='{url}'>{title}</a></b>\n"
            text = text.format(content)

    if text:
        send_text(update, text, keyboard)

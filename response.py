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
                        "/jam_kuliah", "/cuti", "/non_aktif", "/cek_nilai",  
                        "/pindah_kelas", "/pindah_jurusan", "/loker"]

    try:
        command = re.search("/[a-z_]+", message)[0]
        if command in list_of_commands:
            return command
    except:
        return None

def load_data_from_yaml(command):
    """Load data from yaml file"""
    yaml_path = f"scrape_files/data/{command[1:]}.yaml"
    data = yaml.load(open(yaml_path), Loader=yaml.FullLoader)
    return data

def sort_data_by_date_desc(data):
    """Sort data in dict by date in descending order"""
    key = lambda x: dt.strptime(getitem(x[1], "date"), "%d/%m/%Y")
    sorted_data = OrderedDict(sorted(data.items(), key=key, reverse=True))
    return sorted_data

def template_from_file(command_or_callback, from_callback=False):
    """Get template from html file"""
    if from_callback:
        template_path = f"response_templates/callback/{command_or_callback[1:-2]}.html"
    else:
        template_path = f"response_templates/command/{command_or_callback}.html"

    template=Path(template_path).read_text()
    return template

def send_image(context, chat_id, image_path, keyboard=None, caption=None):
    """Send image to user"""
    image = open(image_path, "rb")
    context.bot.sendPhoto(chat_id=chat_id, 
                          photo=image, 
                          reply_markup=keyboard, 
                          caption=caption, 
                          parse_mode=ParseMode.HTML)

def reply_message(update, context, command):
    """Reply message to user"""
    chat_id = update.message.chat.id

    try:
        keyboard = button.create_button(command)
    except:
        keyboard = None

    if command == "/kalendar":
        text = None 
        caption, image_path, _ = load_data_from_yaml(command).values()
        send_image(context, chat_id, image_path, keyboard, caption)
    elif command == "/jam_kuliah":
        image_path = load_data_from_yaml(command)["img_path"]
        send_image(context, chat_id, image_path)
        text = template_from_file(command) # for reply_text, will send text after media
    elif command == "/loker":
        data = load_data_from_yaml(command)
        content = ""
        sorted_data = sort_data_by_date_desc(data)
        for id in sorted_data:
            date, title, url = sorted_data[id].values()
            content += f"🗞 <b>({date})  <a href='{url}'>{title}</a></b>\n"
        text = template_from_file(command).format(content)
    elif command == "/jadwal":
        keyboard = None # remove keyboard, recreate when successful get 'jadwal' data
        text = template_from_file(command)
        message = update.message.text.lower() 
        message_split = message.split(" ", 1) # split command and query
        if message_split[0] == command and len(message_split) == 2: # accept in format '/command <query>'
            query = message_split[1]
            if len(query) >= 5:
                update.message.reply_text(f"Mencari jadwal untuk input '{query}' ...")
                try:
                    data_jadwal = scraping.scraping_jadwal_kuliah(query)
                except Exception as e:
                    update.message.reply_text(dedent(f"""
                        ERROR: Terdapat masalah saat mengakses BAAK\n
                        {e}\n
                        Silahkan hubungi @elmoallistair
                        """), parse_mode=ParseMode.HTML)
                    return None
                if data_jadwal: # successful scraping
                    img_path, caption = data_jadwal
                    keyboard = button.create_button(command)
                    try:
                        text = None # remove text
                        send_image(context, chat_id, img_path, keyboard, dedent(caption))
                    except:
                        text = f"""
                                Terlalu banyak data yang ditemukan untuk input '{query}' 
                                Silahkan gunakan nama kelas atau dosen yang lebih spesifik.
                                """
                else:
                    text = f"Input '{query}' tidak ada dalam database untuk kategori kelas/dosen"
    elif command == "/berita":
        data = load_data_from_yaml(command)
        message = update.message.text.lower()
        message_split = message.split(" ", 1) # split command and query
        if message_split[0] == command and len(message_split) == 2: # accept in format '/command <query>'
            query = message_split[1]
            try:
                content, _, title, _ = data[query].values()
                text = f"<b>{title.upper()}</b>\n\n{content}"
            except:
                keyboard = None # remove keyboard
                text = f"Tidak dapat menemukan berita dengan id: {query}"
        else:
            content = ""
            sorted_data = sort_data_by_date_desc(data)
            for id in sorted_data:
                _, date, title, url = sorted_data[id].values()
                content += f"🗞 <b>({date} - {id})  <a href='{url}'>{title}</a></b>\n"
            text = template_from_file(command).format(content)
    else:
        text = template_from_file(command)

    if text is not None:
        update.message.reply_text(text=dedent(text), 
                                  reply_markup=keyboard, 
                                  parse_mode=ParseMode.HTML, 
                                  disable_web_page_preview=True)
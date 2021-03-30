from collections import OrderedDict
from operator import getitem
from pathlib import Path
from telegram import ParseMode
import scraping
import button
import textwrap
import yaml
import re

def validate_message(message):
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
    yaml_path = f"scrape_files/data/{command[1:]}.yaml"
    data = yaml.load(open(yaml_path), Loader=yaml.FullLoader)
    return data

def get_image_data(command):
    file_path = f"scrape_files/data/{command[1:]}.yaml"
    data = yaml.load(open(file_path), Loader=yaml.FullLoader)
    return list(data.values())

def template_from_file(command_or_callback, from_callback=False):
    if from_callback:
        template=Path(f"response_templates/callback/{command_or_callback[1:-2]}.html").read_text()
    else:
        template=Path(f"response_templates/command/{command_or_callback}.html").read_text()
    return template

def send_image(context, chat_id, image_path, keyboard=None, caption=None):
    image = open(image_path, "rb")
    context.bot.sendPhoto(chat_id=chat_id, 
                          photo=image, 
                          reply_markup=keyboard, 
                          caption=caption, 
                          parse_mode=ParseMode.HTML)

def create_reply(update, context, command):
    chat_id = update.message.chat.id
    text = None
    
    try:
        keyboard = button.create_button(command)
    except:
        keyboard = None

    if command == "/kalendar":
        caption, image_path, _ = get_image_data(command)
        send_image(context, chat_id, image_path, keyboard, caption)
    elif command == "/jam_kuliah":
        text = "Jadwal Kuliah"
        image_path = get_image_data(command)[0]
        send_image(context, chat_id, image_path)
    elif command == "/jadwal":
        message = update.message.text.lower()
        message_split = message.split(" ", 1) 
        if message_split[0] == command and len(message_split) > 1:
            input = message_split[1]
            update.message.reply_text(f"Mencari jadwal untuk input <b>{input}</b>...", parse_mode=ParseMode.HTML)
            data = scraping.scraping_jadwal_kuliah(input)
            if data:
                img_path, caption = data
                send_image(context, chat_id, img_path, keyboard, caption)
            else:
                text = f"Input '{input}' tidak ada dalam database untuk kategori kelas / dosen"
        else:
            text = template_from_file(command)
    elif command == "/berita":
        data = load_data_from_yaml(command)
        message = update.message.text.lower()
        message_split = message.split(" ", 1) 
        if message_split[0] == command and len(message_split) > 1:
            input = message_split[1]
            try:
                title = data[input]["title"]
                content = data[input]["content"]
                text = f"<b>{title.upper()}</b>\n\n{content}"
            except:
                text = f"Tidak dapat menemukan berita dengan id: <b>{input}</b>"
        else:
            content = ""
            sorted_data = OrderedDict(sorted(data.items(), key=lambda x: getitem(x[1], "date"), reverse=True))
            for id in sorted_data.keys():
                _, date, title, url = sorted_data[id].values()
                content += f"🗞 <b>({date} - {id})  <a href='{url}'>{title}</a></b>\n"
            text = template_from_file(command).format(content)
    elif command == "/loker":
        data = load_data_from_yaml(command)
        text = "<b>POSTINGAN LOKER TERBARU</b>\n\n"
        sorted_data = OrderedDict(sorted(data.items(), key=lambda x: getitem(x[1], "date"), reverse=True))
        print(sorted_data)
        for id in sorted_data.keys():
            date, title, url = sorted_data[id].values()
            text += f"🗞 <b>({date})  <a href='{url}'>{title}</a></b>\n"
    else:
        text = template_from_file(command)
    
    update.message.reply_text(text=textwrap.dedent(text), 
                              reply_markup=keyboard, 
                              parse_mode=ParseMode.HTML, 
                              disable_web_page_preview=True)
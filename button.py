from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import yaml

def get_calendar_download_link():
    yaml_path = "scrape_files/data/kalendar.yaml"
    data = yaml.load(open(yaml_path), Loader=yaml.FullLoader)
    return data["url_file"]

def create_button(command, from_callback=False):
    template = {
        "/start":           [("Lihat Dokumentasi","https://github.com/elmoallistair/gunadarma-telegram-bot/blob/main/README.md"),
                             ("Lihat Source Code","https://github.com/elmoallistair/gunadarma-telegram-bot")],
        "/help":            [("Lihat Dokumentasi","https://github.com/elmoallistair/gunadarma-telegram-bot/blob/main/README.md")],
        "/kalendar":        [("Download sebagai PDF", f"{get_calendar_download_link()}")],
        "/berita":          [("Kunjungi Website", "https://berita.gunadarma.ac.id")],
        "/jadwal":          [("Cara Membaca Jadwal", "")],
        "/cuti":            [("Ketentuan dan Prosedur", ""),
                             ("📝  Formulir Cuti Akademik", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/F-CUTI%20New.doc")],
        "/cek_nilai":       [("Ketentuan dan Prosedur", "")],
        "/non_aktif":       [("Ketentuan dan Prosedur", ""),
                             ("📝  Formulir Tidak Aktif Kuliah", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/Formulir%20NonAktif.pdf")],
        "/pindah_kelas":    [("Ketentuan dan Prosedur", ""),
                             ("📝  Formulir Pindah Kelas", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/F-PINKEL%20New.doc")],
        "/pindah_jurusan":  [("Ketentuan dan Prosedur", ""),
                             ("📝  Formulir Pindah Jurusan Fakultas Ekonomi", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/pindah_jurusan_ekonomi.pdf"),
                             ("📝  Formulir Pindah Jurusan Fakultas Ilkom", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/pindah_jurusan_ilkom.pdf"),
                             ("📝  Formulir Pindah Jurusan Fakultas Teknologi Industri]", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/pindah_jurusan_ti.pdf")],
        "/loker":            [("Kunjungi Career Center", "http://career.gunadarma.ac.id/")]
    }
    
    keyboard = []
    if command in template.keys():
        for i, (text,url) in enumerate(template[command]):
            keyboard.append([InlineKeyboardButton(text=text, callback_data=f"{command}_callback_{i}", url=url)])
        return InlineKeyboardMarkup(keyboard)
    return None

def create_button_from_callback(callback_name):
    template = {
        "/cuti_callback_0":            [("📝  Formulir Cuti Akademik", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/F-CUTI%20New.doc")],
        "/non_aktif_callback_0":       [("📝  Formulir Tidak Aktif Kuliah", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/Formulir%20NonAktif.pdf")],
        "/pindah_kelas_callback_0":    [("📝  Formulir Pindah Kelas", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/F-PINKEL%20New.doc")],
        "/pindah_jurusan_callback_0":  [("📝  Formulir Pindah Jurusan Fakultas Ekonomi", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/pindah_jurusan_ekonomi.pdf"),
                                        ("📝  Formulir Pindah Jurusan Fakultas Ilkom", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/pindah_jurusan_ilkom.pdf"),
                                        ("📝  Formulir Pindah Jurusan Fakultas Teknologi Industri]", "https://baak.gunadarma.ac.id/public/file/Administrasi%20Akademik/pindah_jurusan_ti.pdf")]
    }
    
    keyboard = []
    if callback_name in template.keys():
        for i, (text,url) in enumerate(template[callback_name]):
            keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_name, url=url)])
        return InlineKeyboardMarkup(keyboard)
    return None
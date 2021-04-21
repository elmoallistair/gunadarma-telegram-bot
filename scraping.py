from selenium import webdriver 
from selenium.webdriver.chrome.options import Options as ChromeOptions 
import os
import re
import yaml

def set_driver():
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    return driver

def write_to_yaml(data, yaml_path):
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(data, yaml_file)

def screenshot_element(element, img_path):
    screenshot = element.screenshot_as_png
    with open(img_path, "wb") as file:
        file.write(screenshot)

def scraping_kalendar_akademik():
    driver = set_driver()
    driver.get("https://baak.gunadarma.ac.id")
    title = driver.find_element_by_xpath("//div[@class='cell-sm-6 cell-md-6']/h3")
    table = driver.find_element_by_xpath("//table[@class='table table-custom table-primary bordered-table table-striped table-fixed stacktable large-only']") 
    url_download = driver.find_element_by_xpath("//p[@class='text-primary']/a")
    url_file = url_download.get_attribute("href")
    caption = title.text

    img_path = "scrape_files/img/kalendar_akademik.png"
    yaml_path = "scrape_files/data/kalendar.yaml"
    data = {"caption":caption, "img_path":img_path, "url_file": url_file}

    screenshot_element(table, img_path)
    write_to_yaml(data, yaml_path)
    driver.quit() 

def scraping_jam_kuliah():
    driver = set_driver()
    driver.get("https://baak.gunadarma.ac.id/kuliahUjian/6#undefined6")
    table = driver.find_elements_by_xpath("//table[@class='table table-custom table-primary table-fixed stacktable cell-xs-6']")
    
    img_path = "scrape_files/img/jam_kuliah.png"
    yaml_path = "scrape_files/data/jam_kuliah.yaml"
    data = {"img_path":img_path}
    
    screenshot_element(table[0], img_path)
    write_to_yaml(data, yaml_path)
    driver.quit() 
    
def scraping_jadwal_kuliah(class_or_lecturer):
    driver = set_driver()
    driver.get("https://baak.gunadarma.ac.id/jadwal/cariJadKul")
    form_input = driver.find_element_by_xpath("//input[@class='form-search-input form-control']")
    form_submit = driver.find_element_by_xpath("//button[@class='form-search-submit']")
    form_input.send_keys(class_or_lecturer)
    form_submit.click()

    try:
        table = driver.find_element_by_xpath("//table[@class='table table-custom table-primary table-fixed bordered-table stacktable large-only']")
    except:
        return None

    title = driver.find_elements_by_xpath("//h3[@class='veil reveal-sm-block']")[0].text
    notes = driver.find_element_by_xpath("//p[@class='text-md-left']").text
    filename = re.sub(r'[ /]', '_', title).lower()

    caption = f"""
        {title}\n
        Untuk Input : <b>{class_or_lecturer.upper()}</b>
        {notes}
    """

    img_path = f"scrape_files/img/{class_or_lecturer.replace(' ','_')}_jadwal.png"
    screenshot_element(table, img_path)
    driver.quit()

    return img_path, caption

def scraping_berita():
    driver = set_driver()
    driver.get("https://baak.gunadarma.ac.id/berita")
    title_url = driver.find_elements_by_xpath("//div[@class='post-news-body']/h6/a")
    date = driver.find_elements_by_xpath("//span[@class='text-middle inset-left-10 text-italic text-black']")

    post_title = [post.text for post in title_url]
    post_url = [post.get_attribute("href") for post in title_url]
    post_id = [re.search("berita/(\d+)", post).group(1) for post in post_url]
    post_date = [post.text for post in date]
    
    post_content = []
    for url in post_url:
        driver.get(url)
        elements = driver.find_elements_by_xpath("//div[@class='offset-top-30']")
        page_content = elements[0].text
        page_content = re.sub("[ \-\w\(\)\d]+(?:.doc|.pdf)", "", page_content).strip()
        post_content.append(page_content)

    contents = [*zip(post_id, post_title, post_url, post_date, post_content)]
    data = {}
    for id, title, url, date, content in contents:
        data[id] = {"title":title, "url":url, "date":date, "content":content}
    
    yaml_path = "scrape_files/data/berita.yaml"
    write_to_yaml(data, yaml_path)
    driver.quit()

def scraping_loker():
    driver = set_driver()
    driver.get("http://career.gunadarma.ac.id/")
    elements = driver.find_elements_by_xpath("//div[@class='views-field views-field-title']/span/a")

    post_title = [element.text for element in elements]
    post_url = [element.get_attribute("href") for element in elements]
    post_id = [re.search("node/(\d+)", url).group(1) for url in post_url]
    
    post_date = []
    for url in post_url:
        driver.get(url)
        elements = driver.find_elements_by_xpath("//span[@class='meta submitted']")
        date_posted = re.search("\d{2}/\d{2}/\d{4}", elements[0].text)[0]
        post_date.append(date_posted)

    contents = [*zip(post_id, post_title, post_url, post_date)]
    data = {}
    for id, title, url, date in contents:
        data[id] = {"date":date, "title":title, "url":url}
    
    yaml_path = "scrape_files/data/loker.yaml"
    write_to_yaml(data, yaml_path)
    driver.quit()

def start_scraping():
    print("Scraping http://baak.gunadarma.ac.id ...")
    scraping_berita()
    print("- Data 'berita' saved in scrape_files/data/berita.yaml")
    scraping_jam_kuliah()
    print("- Data 'jam_kuliah' saved in scrape_files/data/jam_kuliah.yaml")
    scraping_kalendar_akademik()
    print("- Data 'kalendar' saved in scrape_files/data/kalendar.yaml")
    
    print("Scraping http://career.gunadarma.ac.id ...")
    scraping_loker()
    print("- Data 'loker' saved in scrape_files/data/loker.yaml")

if __name__ == "__main__":
    # update data
    start_scraping()

    # test jadwal
    scraping_jadwal_kuliah("3ka17")
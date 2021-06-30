from selenium import webdriver 
import os
import re
import yaml

def set_driver():
    """Preparing chromedriver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
    # driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    return driver

def open_website(driver, url):
    """Open the website"""
    driver.get(url)
    if driver.title == "":
        raise AssertionError("Error accessing '{url}'")
    return driver

def get_metadata(key):
    """Get url and xpath location from yaml file"""
    data = yaml.load(open("scraping_metadata.yaml"), Loader=yaml.FullLoader)
    return data[key].values()

def write_to_yaml(data, filename):
    """Save scraping result to yaml file"""
    yaml_path = f"scrape_files/data/{filename}.yaml"
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(data, yaml_file)

def screenshot_element(driver, element, img_path):
    """Screenshot element from web page"""
    driver.execute_script("window.scrollTo(0, 475)") # scroll page 
    screenshot = element.screenshot_as_png
    with open(img_path, "wb") as file:
        file.write(screenshot)

def scraping_kalendar_akademik():
    driver = set_driver()
    url, xpath = get_metadata("kalendar")
    try:
        open_website(driver, url)
        caption = driver.find_element_by_xpath(xpath["title"]).text
        table = driver.find_element_by_xpath(xpath["table"])
        url_file = driver.find_element_by_xpath(xpath["file_url"]).get_attribute("href")
        img_path = "scrape_files/img/kalendar_akademik.png"
        data = {"caption":f"<b>{caption}</b>", 
                "img_path":img_path, 
                "url_file":url_file}
        screenshot_element(driver, table, img_path)
        write_to_yaml(data, "kalendar")
        print("Successfull scraping 'kalendar'")
        driver.quit() 
    except Exception as e:
        print(f"Failed scraping 'kalendar': ({e})")

def scraping_jam():
    driver = set_driver()
    url, xpath = get_metadata("jam")
    try:
        open_website(driver, url)
        table = driver.find_elements_by_xpath(xpath["table"])[0]
        img_path = "scrape_files/img/jam.png"
        data = {"img_path":img_path}
        screenshot_element(driver, table, img_path)
        write_to_yaml(data, "jam")
        print("Successfull scraping 'jam'")
        driver.quit()
    except Exception as e:
        print(f"Failed scraping 'jam': {e}")
    
def scraping_jadwal_kuliah(class_or_lecturer):
    driver = set_driver()
    url, xpath = get_metadata("jadwal_kuliah")
    try:
        open_website(driver, url)
        form_input = driver.find_element_by_xpath(xpath["form_input"])
        form_submit = driver.find_element_by_xpath(xpath["form_submit"])
        form_input.send_keys(class_or_lecturer)
        form_submit.click()
        try:
            table = driver.find_element_by_xpath(xpath["table"])
        except:
            return None
        title = driver.find_elements_by_xpath(xpath["title"])[0].text
        valid_from = driver.find_element_by_xpath(xpath["valid_from"]).text
        filename = re.sub(r'[ /]', '_', title).lower()
        caption = f"<b>{title}</b>\n\nUntuk Input : <b>{class_or_lecturer.upper()}</b>\n{valid_from}"
        img_path = f"scrape_files/img/{class_or_lecturer.replace(' ','_')}_jadwal.png"
        driver.execute_script("window.scrollTo(0, 475)")
        screenshot_element(driver, table, img_path)
        driver.quit()
        return img_path, caption
    except Exception as e:
       print(f"Failed scraping 'jadwal_kuliah': {e}")
       print(f"err: {e}")

def scraping_berita():
    driver = set_driver()
    url, xpath = get_metadata("berita")
    try:
        open_website(driver, url)
        title_url = driver.find_elements_by_xpath(xpath["title_and_url"])
        date = driver.find_elements_by_xpath(xpath["date"])
        post_title = [post.text for post in title_url]
        post_url = [post.get_attribute("href") for post in title_url]
        post_id = [re.search("berita/(\d+)", post).group(1) for post in post_url]
        post_date = [post.text for post in date]
        post_content = []
        for url in post_url: # scrape every post
            driver.get(url)
            page_content = driver.find_elements_by_xpath(xpath["page_content"])
            content = page_content[0].text
            content = re.sub("[ \-\w\(\)\d]+(?:.doc|.pdf)", "", content).strip()
            post_content.append(content)
        contents = zip(post_id, post_title, post_url, post_date, post_content)
        data = {}
        for id, title, url, date, content in contents:
            data[id] = {"title":title, "url":url, "date":date, "content":content}
        write_to_yaml(data, "berita")
        driver.quit()
        print("Successfull scraping 'berita'")
    except Exception as e:
        print(f"Failed scraping 'berita': {e}")

def scraping_loker():
    driver = set_driver()
    url, xpath = get_metadata("loker")
    try:
        open_website(driver, url)
        elements = driver.find_elements_by_xpath(xpath["title_and_url"])
        post_title = [element.text for element in elements]
        post_url = [element.get_attribute("href") for element in elements]
        post_id = [re.search("node/(\d+)", url).group(1) for url in post_url]
        post_date = []
        for url in post_url: # scrape every post
            driver.get(url)
            elements = driver.find_elements_by_xpath("//span[@class='meta submitted']")
            date_posted = re.search("\d{2}/\d{2}/\d{4}", elements[0].text)[0]
            post_date.append(date_posted)
        contents = zip(post_id, post_title, post_url, post_date)
        data = {}
        for id, title, url, date in contents:
            data[id] = {"date":date, "title":title, "url":url}
        write_to_yaml(data, 'loker')
        print("Successfull scraping 'loker'")
        driver.quit()
    except Exception as e:
        print(f"Failed scraping 'loker': \n{e}")

def update_all():
    """Update all data"""
    scraping_berita()
    scraping_loker()
    scraping_jam()
    scraping_kalendar_akademik()

if __name__ == "__main__":
    print("Testing scraping...")
    update_all()
    scraping_jadwal_kuliah("3ka17")

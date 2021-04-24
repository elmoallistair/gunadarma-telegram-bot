from selenium import webdriver 
import os
import re
import yaml

def set_driver():
    options = webdriver.FirefoxOptions()
    # options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
    
    # For testing
    # driver = webdriver.Chrome(options=options)
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1920, 1080)

    return driver

def open_website(driver, url):
    """Open the website and check if the website is accessible"""
    driver.get(url)
    if driver.title == "":
        raise AssertionError("Error accessing website")
    return driver

def get_xpath(key):
    """Get xpath location from yaml file"""
    data = yaml.load(open("xpath_location.yaml"), Loader=yaml.FullLoader)
    return data[key]

def write_to_yaml(data, yaml_path):
    """Save scraping result to yaml file"""
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(data, yaml_file)

def screenshot_element(element, img_path):
    """Screenshot element from web page"""
    screenshot = element.screenshot_as_png
    with open(img_path, "wb") as file:
        file.write(screenshot)

def scraping_kalendar_akademik():
    driver = set_driver()
    xpath = get_xpath("kalendar")

    try:
        open_website(driver, "https://baak.gunadarma.ac.id")
        caption = driver.find_element_by_xpath(xpath["title"]).text
        table = driver.find_element_by_xpath(xpath["table"])
        url_file = driver.find_element_by_xpath(xpath["url"]).get_attribute("href")

        img_path = "scrape_files/img/kalendar_akademik.png"
        yaml_path = "scrape_files/data/kalendar.yaml"
        screenshot_element(table, img_path)
        
        data = {"caption":caption, "img_path":img_path, "url_file": url_file}
        write_to_yaml(data, yaml_path)

        print("Successfull scraping 'kalendar'")
        driver.quit() 
    
    except Exception as e:
        print(f"Failed scraping 'kalendar' ({e})")

def scraping_jam_kuliah():
    driver = set_driver()
    xpath = get_xpath("jam_kuliah")
    
    try:
        open_website(driver, "https://baak.gunadarma.ac.id/kuliahUjian/6#undefined6")
        table = driver.find_elements_by_xpath(xpath["table"])
        
        img_path = "scrape_files/img/jam_kuliah.png"
        yaml_path = "scrape_files/data/jam_kuliah.yaml"
        screenshot_element(table[0], img_path)
        
        data = {"img_path":img_path}
        write_to_yaml(data, yaml_path)

        print("Successfull scraping 'jam_kuliah'")
        driver.quit()

    except Exception as e:
        print(f"Failed scraping 'jam_kuliah'\n{e}")
    
def scraping_jadwal_kuliah(class_or_lecturer):
    driver = set_driver()
    xpath = get_xpath("jadwal_kuliah")
    try:
        open_website(driver, "https://baak.gunadarma.ac.id/jadwal/cariJadKul")
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

        screenshot_element(table, img_path)
        driver.quit()

        return img_path, caption

    except Exception as e:
       raise e

def scraping_berita():
    driver = set_driver()
    xpath = get_xpath("berita")
    
    try:
        open_website(driver, "https://baak.gunadarma.ac.id/berita")
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

        yaml_path = "scrape_files/data/berita.yaml"
        write_to_yaml(data, yaml_path)
        driver.quit()
        print("Successfull scraping 'berita'")

    except Exception as e:
        print(f"Failed scraping 'berita'\n{e}")

def scraping_loker():
    driver = set_driver()
    xpath = get_xpath("loker")
    
    try:
        open_website(driver, "http://career.gunadarma.ac.id/")
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

        yaml_path = "scrape_files/data/loker.yaml"
        print(data)
        write_to_yaml(data, yaml_path)

        print("Successfull scraping 'loker'")
        driver.quit()

    except Exception as e:
        print(f"Failed scraping 'berita'\n{e}")

def start_scraping():
    """Start scraping"""
    scraping_berita()
    scraping_jam_kuliah()
    scraping_kalendar_akademik()
    scraping_loker()

if __name__ == "__main__":
    print("Testing scraping...")
    start_scraping()
    # scraping_jadwal_kuliah("3ka17")
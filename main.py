import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import requests
import time
import re


# Function definitions
def format_name(date, resource_types, file_name):
    resource_types = re.sub(r",\s+", '-', resource_types)  # Replaces commas followed by a space with a dash
    resource_types = re.sub(r"\s+", '_', resource_types)  # Replaces left spaces with an underscore
    resource_types = '[' + resource_types + ']'
    date = '[' + date + ']'
    return date + '-' + resource_types + '-' + file_name


def download_files(file_download_path):
    table_data_elements = driver.find_elements(By.CSS_SELECTOR, '[role=row][id]')

    for element in table_data_elements:
        download_button_element = element.find_element(By.CSS_SELECTOR, '[aria-label=descargar]')
        print('Download Button href: ' + download_button_element.get_attribute('href'))
        response = requests.get(download_button_element.get_attribute('href'))  # Request file

        resource_type_title_element = element.find_element(By.CSS_SELECTOR, '[data-title="Tipo de recurso"]')
        resource_type = resource_type_title_element.get_property('innerText')
        date = element.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
        file_name = download_button_element.get_attribute('href').rsplit('/', 1)[-1]
        formated_file_name = format_name(date, resource_type, file_name)

        print('File name: ' + formated_file_name)

        file_path = file_download_path + '/' + formated_file_name

        if os.path.exists(file_path):  # Avoids downloading the file if it already exists
            print('The file already exists. Skipping.')
            continue

        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print('File downloaded successfully')
        else:
            print('Failed to download file')


# End of function definitions


# This script assumes you are on linux and have Chromium installed. Have fun!


# This is where you should declare the path to your webdriver.
driver_path = r'/usr/lib/chromium/chromedriver'
os.environ['PATH'] += driver_path  # Adds the driver path to the session's PATH variable
options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument('--headless')  # Comment this line out if you need to see the browser window
driver = webdriver.Chrome(options)

print('Getting web page...')
driver.get('https://www.argentina.gob.ar/salud/recursos')
try:
    # First we wait for the topic selection to show up, it is a WebElement type object
    topic_web_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'tema'))
    )
    # And then we make a Select class object with it to iterate it later
    topic_select_element = Select(driver.find_element('name', 'tema'))
    # The "Intended Public" filter is reset whenever the topic filter is
    intended_public_select_element = Select(driver.find_element('name', 'destinatario'))

    print('\nPage has been loaded correctly.')
    time.sleep(1)
    print('Topics found: ' + str(topic_select_element.options.__len__()))
    time.sleep(1)
    print('The download process is about to start.')
    time.sleep(2)
except Exception as e:
    print("\nAn unexpected error has ocurred, please check it and try again:")
    print(e)
    exit()

download_path = r'./resources'
if not os.path.exists(download_path):
    os.makedirs(download_path)

for i in range(1, topic_select_element.options.__len__(), 1):  # Topic selection loop, skipping the first "all" option
    topic_select_element.select_by_index(i)

    try:
        intended_public_select_element.select_by_value('Profesionales y población')
    except NoSuchElementException:
        try:
            intended_public_select_element.select_by_value('Materiales para población')
        except NoSuchElementException:
            print("\nThere are not any documents intended for the general public. Skipping to next topic...")
            continue
    time.sleep(0.5)

    # Should evaluate using the i counter instead of first_selected_option
    current_topic = topic_select_element.first_selected_option.get_property('text')
    print('\nCurrent topic: ' + current_topic)
    next_page_li = driver.find_element('id', 'ponchoTable_next')
    if 'disable' in next_page_li.get_attribute('class'):
        print('\nThis topic had only one page\n')
    else:
        print('\nThis topic has more than one page\n')

    current_topic = current_topic.replace(" ", "_")
    topic_download_path = download_path + '/' + current_topic
    if not os.path.exists(topic_download_path):
        os.makedirs(topic_download_path)
    download_files(topic_download_path)

    while 'disable' not in next_page_li.get_attribute('class'):  # Checks if there are pages left
        next_page_element = next_page_li.find_element(By.TAG_NAME, 'a')
        ActionChains(driver).move_to_element(next_page_element).click(next_page_element).perform()
        download_files(topic_download_path)
        # The pagination elements in the table are generated again after a page change
        next_page_li = driver.find_element('id', 'ponchoTable_next')  # This is to use the new next page element

print('All files have been downloaded and can be found in the "resources" folder.')
print('Gracias, vuelva prontos.')
driver.quit()

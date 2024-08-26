import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import requests
import time

#Function definitions
def download_files(download_path):
    download_elements = driver.find_elements(By.CSS_SELECTOR, '[aria-label=descargar]')
    for element in download_elements:
        print('Element href: '+element.get_attribute('href'))
        response = requests.get(element.get_attribute('href'))
        file_name = element.get_attribute('href').rsplit('/', 1)[-1]
        print('File name: ' + file_name)

        file_path = download_path + '/' + file_name

        if os.path.exists(file_path): #Avoids downloading the file if it already exists
            print('The file already exists. Skipping.')
            continue

        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print('File downloaded successfully')
        else:
            print('Failed to download file')

#End of function definitions


#This script assumes you are on linux and have Chromium installed. Have fun!


#This is where you should declare the path to your webdriver.
driver_path = r'/usr/lib/chromium/chromedriver'
os.environ['PATH'] += driver_path #Adds the driver path to the session's PATH variable
options = webdriver.ChromeOptions()
options.add_argument('--incognito')
#options.add_argument('--headless') #Comment this line out if you need to see the browser window
driver = webdriver.Chrome(options)

print('Getting web page...')
driver.get('https://www.argentina.gob.ar/salud/recursos')
try:
    #First we wait for the topic selection to show up, it is a WebElement type object
    topic_web_element = WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.NAME, 'tema'))
    )
    #And then we make a Select class object with it to iterate it later
    topic_select_element = Select(driver.find_element('name', 'tema'))
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

for i in range (1, topic_select_element.options.__len__(), 1): #Topic selection loop, skipping the first "all" option
    topic_select_element.select_by_index(i)
    time.sleep(0.5)

    # Should evaluate using the i counter instead of first_selected_option
    current_topic = topic_select_element.first_selected_option.get_property('text')
    print('\nCurrent topic: ' + current_topic)
    current_topic = current_topic.replace(" ","_")
    topic_download_path = download_path + '/' + current_topic
    if not os.path.exists(topic_download_path):
        os.makedirs(topic_download_path)
    download_files(topic_download_path)

    next_page_li = driver.find_element('id', 'ponchoTable_next')
    if 'disable' in next_page_li.get_attribute('class'):
        print('\nThis topic has only one page\n')
    else:
        print('\nThis topic has more than one page\n')
    while 'disable' not in next_page_li.get_attribute('class'): #Checks if there are pages left
        next_page_element = next_page_li.find_element(By.TAG_NAME, 'a')
        ActionChains(driver).move_to_element(next_page_element).click(next_page_element).perform()
        download_files(topic_download_path)
        #The pagination elements in the table are generated again after a page change
        next_page_li = driver.find_element('id', 'ponchoTable_next') #This is to use the new next page element

print('All files have been downloaded and can be found in the "resources" folder.')
print('Gracias, vuelva prontos.')
driver.quit()

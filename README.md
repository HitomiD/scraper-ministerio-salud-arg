# scraper-ministerio-salud-arg
This is a simple python script for PDF file download automation.

The purpose of this script is to automate the file downloading process from the public resources section of the official website from the Ministry of Health of Argentina.

This website consists of a dynamically generated table, so Selenium was necessary to deal with the JS execution. You will need to provide a browser and its webdriver.
All other simple HTTP requests are handled with the Requests library.

This script was made to run in linux assuming that Chromium (which provides its own webdriver by default) is already installed. For any other OS and browser configuration
you will need to tweak the script to change the path structure and the webdriver accordingly.

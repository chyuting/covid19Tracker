import time
from selenium import webdriver

chrome_driver_path = 'C:/Users/pc/Downloads/chromedriver_win32/chromedriver.exe'
driver = webdriver.Chrome(chrome_driver_path)  # Optional argument, if not specified will search path.
driver.get('http://www.google.com/')
time.sleep(5) # Let the user actually see something!
search_box = driver.find_element_by_name('q')
search_box.send_keys('ChromeDriver')
search_box.submit()
time.sleep(5) # Let the user actually see something!
driver.quit()
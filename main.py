"""
requires :
    - selenium
    - webdriver-manager
    - instagrapi

"""

import atexit
import os
import sys
import time
import urllib.request

from pathlib import Path
from instagrapi import Client

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# run chrome headless
chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# register quit function to safely quit the driver
atexit.register(driver.quit)

# setup download
base_path = "clips"
clip_url = ""
clip_name = clip_url.rpartition("/")[-1]
encoding = "mp4"
file_name = os.path.join(base_path, f"{clip_name}.{encoding}")

# get clip url page
driver.get(clip_url)

# find video tag
s = driver.find_element(By.TAG_NAME, "video")

MAX_TIME_OUT = 10
timeout_counter = 0

src = s.get_dom_attribute("src")

# loop until DOM is loaded
while src is None:
    src = s.get_dom_attribute("src")

    time.sleep(0.2)
    timeout_counter += 1

    if timeout_counter > MAX_TIME_OUT:
        raise ConnectionError("DOM not loaded in time. Try Increasing MAX_TIME_OUT.")

# quit driver (at exit is for errors)
driver.quit()


# progress hook for download
def hook(count, block_size, total_size, filename):
    progress = int(count * block_size * 100 / total_size)
    sys.stdout.write(f"\r{filename} [{'#' * progress + ('.' * (100 - progress))}] %d%%" % progress)
    sys.stdout.flush()


# create output dir
if not os.path.exists(base_path):
    os.makedirs(base_path)

# download file
urllib.request.urlretrieve(src, file_name, reporthook=lambda *args: hook(*args, file_name))
sys.stdout.write("\n")

# upload file to instagram
username = ''
password = ''
text = 'CAPTION CAPTION CAPTION #hash #tag #wow'

# create client object and upload file
client = Client()
client.login(username, password)
client.video_upload(path=Path(file_name), caption=text)

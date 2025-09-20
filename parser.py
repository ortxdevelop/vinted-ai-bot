import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlencode
import pickle
import requests
import time
import json
import os
from fastai.vision.all import *
from io import BytesIO
import warnings
import logging

from config import *

# Config

warnings.filterwarnings("ignore", category=UserWarning, module="fastai.learner")
learn = load_learner('big_pony_model.pkl')
driver = None


def start_driver():
    global driver
    if driver is None:
        options = uc.ChromeOptions()
        options.add_argument(CHROME_PROFILE)
        options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        driver = uc.Chrome(options=options, headless=True, use_subprocess=True)
    return driver

# Loading seen file

try:
    with open(SEEN_FILE, 'r') as f:
        seen_links = set(json.load(f))
except:
    seen_links = set()

def save_seen():
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(seen_links), f)

def clear_seen_file():
    with open(SEEN_FILE, "w") as f:
        f.write("[]") 
    global seen_links
    seen_links.clear()

# Send telegram message

def send_telegram(image_url, caption):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
    data = {
        "chat_id" : CHAT_ID,
        "photo" : image_url,
        "caption" : caption,
        "parse_mode" : "HTML"
    }
    try:
        r = requests.post(url, params=data)
        if not r.ok:
            logging.error("[!] Error with sending a photo ", r.text)
    except Exception as e:
        logging.error("[!] Error with sending a photo ", e)


# Vinted parser

def check_vinted(driver):
    try:
        driver.get("https://vinted.pl")
        time.sleep(10)
        sent_messages = 0
        for term in SEARCH_TERMS:

            params = {
                "search_text" : term,
                "order" : "from_low_to_high",
                "catalog_ids" : 5,
                "category_id" : 1907,
                "price_from" : PRICE_FROM,
                "currency" : CURRENCY,
                "price_to" : PRICE_TO,
                "per_page" : 960,
                "page" : 1
            }

            query_string = urlencode(params)

            try:
                driver.get(f"{BASE_URL}?{query_string}")
            except Exception as e:
                logging.error(f"[!] Request error {e}")
                continue
            try:
                data_text = driver.execute_script("return document.body.innerText")
            except:
                logging.error("Error with an element")

            try:
                data = json.loads(data_text)
            except json.JSONDecodeError as e:
                logging.error(f"[!] JSON parsing error: {e}")

            items = data.get("items", [])

            count = 0

            for item in items:
                item_id = item.get("id")
                url = f"https://www.vinted.pl/items/{item_id}"

                if url in seen_links:
                    continue
                
                # Price

                price_info = item.get("total_item_price", {})
                price = price_info.get("amount", 0)
                currency = price_info.get("currency_code", "")  

                # Condition

                condition =  item.get("status", "").lower() 
                if condition not in CONDITIONS:
                    continue

                # Size

                size =  item.get("size_title", "")
                if size not in SIZES:
                    continue

                # Getting photo url and title

                image_url = item.get("photo", {}).get("full_size_url", "")
                title = item.get("title", "Untitled")

                # Checking price

                if item.get("price", {}).get("currency_code") != CURRENCY:
                    continue

                img = PILImage.create(BytesIO(requests.get(image_url).content))
                pred_class, pred_idx, probs = learn.predict(img)
                if pred_class != 'big_pony':
                        continue

                # Message structure

                caption = (
                    f"<b>{title}</b>\n"
                    f"💰{price} {currency}\n"
                    f"🧵Size: {size}\n"
                    f"👾Condition: {condition.capitalize()}\n"
                    f"🔗<a href='{url}'>Open the product</a>"
                )

                send_telegram(image_url, caption)
                seen_links.add(url)
                count += 1
                sent_messages += 1

                if count >= 2:
                    break


            save_seen()
        return sent_messages
    except Exception as e:
        logging.error(f"Error was occured {e}")

# Launching

# if __name__ == "__main__":
#     driver = start_driver()
#     check_vinted(driver)
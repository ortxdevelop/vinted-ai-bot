import undetected_chromedriver as uc
import time
from config import CHROME_PROFILE


options = uc.ChromeOptions()
options.add_argument(CHROME_PROFILE)

driver = uc.Chrome(options=options, use_subprocess=True)

driver.get("https://www.vinted.pl/")

time.sleep(100)
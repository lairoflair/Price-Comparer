from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROMEDRIVER_PATH = r"C:\chromedriver-win64\chromedriver.exe"

options = Options()
# Try first with headless disabled, enable later if needed
# options.add_argument("--headless")

# Pretend to be a real Chrome browser
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Hide "Chrome is being controlled by automated test software"
options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
options.add_experimental_option("useAutomationExtension", False)

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# Remove navigator.webdriver flag (extra stealth)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
    """
})

site = "https://genius.com/Maroon-5-payphone-lyrics"
site = "https://genius.com/Chief-keef-love-sosa-lyrics"
try:
    driver.get(site)

    wait = WebDriverWait(driver, 10)
    lyrics_containers = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-lyrics-container='true']"))
    )

    lyrics = "\n".join([el.text for el in lyrics_containers])
    print(lyrics if lyrics.strip() else "⚠️ No lyrics found.")

except Exception as e:
    print("Error:", str(e))
finally:
    driver.quit()


# import requests
# from bs4 import BeautifulSoup

# url = "https://genius.com/Maroon-5-payphone-lyrics"
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                   "AppleWebKit/537.36 (KHTML, like Gecko) "
#                   "Chrome/120.0.0.0 Safari/537.36"
# }

# resp = requests.get(url, headers=headers)
# soup = BeautifulSoup(resp.text, "html.parser")

# # Grab all divs that contain lyrics
# lyrics_divs = soup.find_all("div", {"data-lyrics-container": "true"})
# lyrics = "\n".join(div.get_text(separator="\n") for div in lyrics_divs)

# print(lyrics if lyrics.strip() else "⚠️ No lyrics found.")

import requests
# from paapi5_python_sdk.api.default_api import DefaultApi
# from paapi5_python_sdk.models import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
# from playwright.sync_api import sync_playwright
import time
import random

defaultPostalCode = "M5V2T6"
CHROMEDRIVER_PATH = r"C:\chromedriver-win64\chromedriver.exe"
# #amazon stuff
# access_key = "YOUR_ACCESS_KEY"
# secret_key = "YOUR_SECRET_KEY"
# partner_tag = "YOUR_ASSOCIATE_TAG"
# host = "webservices.amazon.ca"
# region = "ca"

def create_driver():
    options = Options()
    # options.add_argument("--headless")  # enable later
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    # options.add_argument("--user-data-dir=C:/Selenium/Profile")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # Stealth
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
        """
    })

    return driver

#works
def scrape_bestbuy(driver):
    # try:
        wait = WebDriverWait(driver, 10)
        
        # products container
        product_container = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div[class *="productCard"]')
            )
        )
        
        products = []
        
        for product in product_container:
            try:
                link = product.find_element(By.CSS_SELECTOR, 'a[role="link"][itemprop="url"]').get_attribute('href')
                price = product.find_element(By.CSS_SELECTOR, 'div[class *="productPricingContainer"] > span[data-automation="product-price"] > span[class*="style-module_screenReaderOnly"]').text
                name = product.find_element(By.CSS_SELECTOR, '[class *= productItemName][itemprop="name"]').text
                
                products.append({
                    'name': name,
                    'price': price,
                    'link': link
                })
            except Exception as e:
                print(f"→ Error extracting product details: {e}")
        return products

def bestbuy_search(product_name, driver):
    base_url = "https://www.bestbuy.ca/en-ca/search?search="
    query = product_name.replace(" ", "+")
    url = f"{base_url}{query}"
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    try:
        availability_button = wait.until(
            EC.element_to_be_clickable(
                    (By.ID, 'availability-toggle')
                )
            )
        driver.execute_script("arguments[0].click();", availability_button)
        
        bestbuyOnly_button = wait.until(
            EC.element_to_be_clickable(
                    (By.ID, 'bestbuy-only-toggle')
                )
            )
        driver.execute_script("arguments[0].click();", bestbuyOnly_button)
        
        scroll_to_bottom(driver, pause=1)
        
        return scrape_bestbuy(driver)

    except Exception as e:
        print(f"BestBuy Search → Error: {e}")
        return []

def scroll_to_bottom(driver, pause=1):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)  # wait for products to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # reached the bottom
        last_height = new_height

#nope
def scrape_amazon(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    price = soup.find("span", {"class": "a-price-whole"})
    availability = soup.find("div", {"id": "availability"})
    return {
        "price": price.text if price else None,
        "availability": availability.text.strip() if availability else None
    }
# attempt using playwright
# def canadiantire_search(product_name, postal_code=defaultPostalCode):
    base_url = "https://www.canadiantire.ca/en/search-results.html?q="
    query = product_name.replace(" ", "+")
    url = f"{base_url}{query}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # set False to watch
        
        context = browser.new_context(
            permissions=["geolocation"],
            geolocation={"latitude": 43.6532, "longitude": -79.3832},
        )
        
        page = context.new_page()
        page.goto(url)
        print ("Page loaded:", url)

        try:
            close_banner = page.query_selector('button[aria-label="Close"]')
            if close_banner:
                close_banner.click()
        except:
            pass


        # Wait for the postal code popup and fill it in
        try:
            print ("Filling postal code:", postal_code)
            postal_input_button = page.wait_for_selector(
                'button.nl-store-locator--section-button[dap-wac-value="Store Locator"]', 
                state="visible", 
                timeout=5000
            ).nth(1)
            print ("Postal code button found")
            postal_input_button.click()
            
            postal_input = page.wait_for_selector('input[id = "nl-store-locator-search-box"]', timeout=5000)
            postal_input.fill(postal_code)
            postal_input_autocomplete_button = page.wait_for_selector('button[class *= "nl-autocomplete-container"]', timeout=5000)
            postal_input_autocomplete_button.click()
            selected_store_button = page.wait_for_selector('button:hastext("Select this store")', timeout=5000)
            selected_store_button.click()
            in_stock_button = page.wait_for_selector('button:has-text("In Stock")', timeout=5000)
            in_stock_button.click()
            page.wait_for_timeout(2000)  # wait for prices to update
        except Exception as e:
            # If no postal code popup, continue
            print("postal error", e)
            return []

        # Wait for product grid to load
        page.wait_for_selector('div.product-tile')

        products = []
        product_cards = page.query_selector_all('div.product-tile')

        for card in product_cards:
            try:
                name_el = card.query_selector('a.product-title-link')
                price_el = card.query_selector('span.price')  # may include sale prices
                link = "https://www.canadiantire.ca" + name_el.get_attribute("href") if name_el else None
                name = name_el.inner_text().strip() if name_el else None
                price = price_el.inner_text().strip() if price_el else None

                products.append({
                    "name": name,
                    "price": price,
                    "link": link
                })
            except Exception as e:
                print(f"→ Error extracting product: {e}")

        browser.close()
        return products
    
#works
def canadiantire_search(product_name, driver, postal_code="M5H 2N2"):
    """
    Search Canadian Tire for a product, set the store via postal code, and scrape product info.
    Requires an existing Selenium driver instance.
    """
    base_url = "https://www.canadiantire.ca/en/search-results.html?q="
    query = product_name.replace(" ", "+")
    url = f"{base_url}{query}"
    driver.get(url)
    print("Page loaded:", url)

    wait = WebDriverWait(driver, 10)

    # Close any banners/popups
    try:
        close_banner = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close"]')
        if close_banner.is_displayed():
            close_banner.click()
    except:
        pass

    # Click the Store Locator button
    try:
        store_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.nl-store-locator--section-button[dap-wac-value="Store Locator"]')
        for button in store_buttons:
            if button.is_displayed() and button.is_enabled():
                button.click()
                break
        else:
            print("No visible Store Locator button found")
            return []
    except Exception as e:
        print("Error clicking Store Locator:", e)
        return []

    # Enter postal code and select store
    try:
        
        postal_input = wait.until(
            EC.visibility_of_element_located((By.ID, "nl-store-locator-search-box"))
        )
        postal_input.clear()
        postal_input.send_keys(postal_code)
        time.sleep(2)
        autocomplete_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class*="nl-autocomplete-container"]'))
        )
        time.sleep(1)
        autocomplete_button.click()
        
        time.sleep(1) 
        select_store_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Select this store"]'))
        )
         # slight delay to ensure button is clickable
        time.sleep(1) 
        select_store_button.click()

        print("Store selected, setting availability filter...")
        
        in_stock_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[span[text()="In Stock At My Store"]]'))
        )
        in_stock_button.click()

        print("done")
        time.sleep(2)  # wait for product grid to update

    except Exception as e:
        print("Postal code popup error or elements not found:", e)
        return []

    # Scrape products
    products = []
    SCROLL_PAUSE_TIME = 1  # seconds
    last_height = driver.execute_script("return document.body.scrollHeight")

    seen_cards = set()  # track cards we already processed

    while True:
        # Scroll down a bit
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        # Get all product cards currently in view
        product_cards = driver.find_elements(By.CSS_SELECTOR, 'li[class*="nl-product__content"]')

        for card in product_cards:
            card_id = card.get_attribute("id")
            if card_id in seen_cards:
                continue  # already processed
            seen_cards.add(card_id)

            try:
                # Get link
                link = card.find_element(By.CSS_SELECTOR, 'a.prod-link').get_attribute('href')

                # Get brand and name
                brand = card.find_element(By.CSS_SELECTOR, 'span[class*="nl-product__brand"]').text.strip()
                name_text = card.find_element(By.CSS_SELECTOR, 'div[class*="nl-product-card__title"]').text.strip()
                name = f"{brand} {name_text}" if brand else name_text

                # Wait for priceTotal to appear (up to 5 seconds per card)
                try:
                    price_element = WebDriverWait(card, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'span[data-testid="priceTotal"]'))
                    )
                    price = price_element.text.strip()
                except:
                    price = "n/a"

                products.append({
                    'name': name,
                    'price': price,
                    'link': link
                })
                print(name, price, link)

            except Exception as e:
                print("Skipped a product:", e)

        # Check if we've reached the bottom
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    # time.sleep(20)
    print("postalcode:", postal_code)
    return products

#cloudflare blocks selenium
def rona_search(product_name, driver, postal_code=defaultPostalCode):
    url = "https://www.rona.ca/en"
    driver.get(url)
    print("Page loaded:", url)

    wait = WebDriverWait(driver, 10)

    try:
        searchbar = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'label[class *= "SearchBar"] > input[placeholder *= "What are you looking for"]'))
        )
    except Exception as e:
        print("Search bar not found:", e)
        return []
    time.sleep(random.uniform(0.05, 0.5))
    searchbar.clear()
    time.sleep(random.uniform(0.05, 0.5))
    for char in product_name:
        searchbar.send_keys(char)
        time.sleep(random.uniform(0.05, 0.5))  # simulate human typing with slight randomness
    time.sleep(random.uniform(0.05, 0.5))
    searchbar.send_keys(Keys.ENTER)
    # Close any banners/popups
    
    time.sleep(20)
    try:
        close_banner = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close"]')
        if close_banner.is_displayed():
            close_banner.click()
    except:
        pass

    # Click the Store Locator button
    try:
        store_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.nl-store-locator--section-button[dap-wac-value="Store Locator"]')
        for button in store_buttons:
            if button.is_displayed() and button.is_enabled():
                button.click()
                break
        else:
            print("No visible Store Locator button found")
            return []
    except Exception as e:
        print("Error clicking Store Locator:", e)
        return []

    # Enter postal code and select store
    try:
        postal_input = wait.until(
            EC.visibility_of_element_located((By.ID, "nl-store-locator-search-box"))
        )
        postal_input.clear()
        postal_input.send_keys(postal_code)
        time.sleep(2)
        autocomplete_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class*="nl-autocomplete-container"]'))
        )
        time.sleep(1)
        autocomplete_button.click()
        
        time.sleep(1) 
        select_store_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Select this store"]'))
        )
         # slight delay to ensure button is clickable
        time.sleep(1) 
        select_store_button.click()

        print("Store selected, setting availability filter...")
        
        in_stock_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[span[text()="In Stock At My Store"]]'))
        )
        in_stock_button.click()

        print("done")
        time.sleep(2)  # wait for product grid to update

    except Exception as e:
        print("Postal code popup error or elements not found:", e)
        return []

    products = []
    return products
   
   
#work in progress 
def homedepot_search(product_name, driver, postal_code=defaultPostalCode):
    url = "https://www.homedepot.ca/en/home.html"
    driver.get(url)
    print("Page loaded:", url)

    wait = WebDriverWait(driver, 10)
    products = []
    try:
        searchbar = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="search"][placeholder="What can we help you find?"]'))
        )
    except Exception as e:
        print("Search bar not found:", e)
        return products
    
    # time.sleep(0.29)
    searchbar.clear()
    # time.sleep(0.23)
    for char in product_name:
        searchbar.send_keys(char)
        # time.sleep(random.uniform(0.05, 0.15))  # simulate human typing with slight randomness
    # time.sleep(1.23)
    searchbar.send_keys(Keys.ENTER)
    
    try:
        close_banner = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close"]')
        if close_banner.is_displayed():
            close_banner.click()
    except:
        pass
    
    try:
        location_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role = "button"][id *= "store-hours"]'))
        )
        location_button.click()
        time.sleep(1)
        
        changeStoreButton = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//a[@role="button" and contains(text(), "Change Store")]'))
        )
        changeStoreButton.click()
        time.sleep(1)
        
        postal_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Postal Code, City, or Store Number"]'))
        )
        postal_input.clear()
        postal_input.send_keys(postal_code)
        postal_input.send_keys(Keys.ENTER)
        time.sleep(1)
        
        selectFirst = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "acl-button")]//span[contains(text(), "Select")]'))
        )
        
        selectFirst.click()
        
        inStock_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="stock"]'))
        )
        driver.execute_script("arguments[0].click();", inStock_button)
        time.sleep(2)  # wait for store to update
    
    except Exception as e:
        print("Postal code popup error or elements not found:", e)
        return products
    time.sleep(1)
    
    try:
        SCROLL_PAUSE_TIME = 2
        seen_cards = set()
        products = []

        prev_count = 0
        while True:
            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            # Collect cards
            product_cards = driver.find_elements(By.CSS_SELECTOR, 'article[id*="productCardIndex"]')
            print(f"Found {len(product_cards)} products")

            for card in product_cards:
                card_id = card.get_attribute("id")
                if card_id in seen_cards:
                    continue
                seen_cards.add(card_id)

                try:
                    link = card.find_element(By.CSS_SELECTOR, 'a.acl-product-card__title-link').get_attribute('href')
                    name = card.find_element(By.CSS_SELECTOR, 'a.acl-product-card__title-link').get_attribute('title')
                    try:
                        price_element = card.find_element(By.CSS_SELECTOR, 'div[class*="acl-product-card__price"] span.ng-star-inserted')
                        price = price_element.text.strip()
                    except:
                        price = "n/a"

                    products.append({"name": name, "price": price, "link": link})
                    print(name, price, link)
                except Exception as e:
                    print("Skipped a product:", e)

            # Stop when no new products appear
            if len(product_cards) == prev_count:
                break
            prev_count = len(product_cards)

    except Exception as e:
        print(f"Error locating product cards: {e}")

    print("postalcode:", postal_code)
    return products

def staples_search(product_name, driver, postal_code=defaultPostalCode):
    # url = "https://www.staples.ca/en"
    url = f"https://www.staples.ca/search?query={product_name.replace(' ', '+')}"
    driver.get(url)
    print("Page loaded:", url)

    wait = WebDriverWait(driver, 10)
    products = []
    # 
    try:
        print("Starting Setting Up")

        # 1️⃣ Click the Store Locator modal
        location_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.StoreLocatorModal'))
        )
        print("location_button found and clickable")
        location_button.click()

        # 2️⃣ Input postal code / city
        location_input = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, 'input.input__element[placeholder="Search store by postal code or city"]'
            ))
        )
        print("location_input found and visible")
        location_input.clear()
        location_input.send_keys(postal_code)
        location_input.send_keys(Keys.ENTER)  # safer than clicking search button

        # 3️⃣ Wait for store results to load
        make_my_store_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//div[contains(@class,"store")]//button[contains(@class,"select-store-button-container") and normalize-space(text())="Make My Store"]'
            ))
        )
        print("make_my_store_button found and clickable")

        # Scroll into view in case element is covered
        # driver.execute_script("arguments[0].scrollIntoView(true);", make_my_store_button)
        time.sleep(0.5)  # small pause after scrolling
        make_my_store_button.click()

        print("Done Setting Up")

    except Exception as e:
        print(f"Staples Search → Error: {e}")
        return products
    print("Done Setting Up")
    
    #scraping products
    try:
        product_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.ais-hits--item'))
        )
        print(f"Found {len(product_cards)} products")
        
        for card in product_cards:
            try:
                try:
                    link = card.find_element(By.CSS_SELECTOR, 'a.product-link.product-thumbnail__title').get_attribute('href')
                except:
                    link = "n/a"
                try:
                    name = card.find_element(By.CSS_SELECTOR, 'a.product-link.product-thumbnail__title').text.strip()
                    
                except:
                    name = "n/a"
                
                try:
                    price_element = card.find_element(By.CSS_SELECTOR, 'span.money.pre-money')
                    price = price_element.text.strip()
                except:
                    price = "n/a"
                
                products.append({'name': name, 'price': price, 'link': link})
                print(f"name: {name}, price: {price}, link: {link}")
            except Exception as e:
                print("Skipped a product:", e)
    except Exception as e:
        print(f"Error locating product cards: {e}")
        return products
    return products
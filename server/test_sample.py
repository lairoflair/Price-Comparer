from scraper import bestbuy_search, scrape_bestbuy, create_driver
from scraper import canadiantire_search
from scraper import rona_search
from scraper import homedepot_search
from scraper import staples_search
if __name__ == "__main__":
    driver = create_driver()  # initialize driver once


    postalCode = "M5V3Y2"
    sites = [
        # "https://www.bestbuy.ca/en-ca/product/asus-prime-radeon-rx-9070-oc-16gb-gddr6-video-card/19204851",
        # "https://www.bestbuy.ca/en-ca/product/asus-prime-radeon-rx-9070-xt-oc-16gb-gddr6-video-card/19177948"
        "https://www.bestbuy.ca/en-ca/search?path=category%253AComputers%2B%2526%2BTablets%253Bsoldandshippedby0enrchstring%253ABest%2BBuy&search=rx9070xt"
    ]


    # staples, rona, home depot, amazon, walmart, costco
    # for site in sites:
    #     scrape_bestbuy(site, driver)

    # result = bestbuy_search("rx9070xt", driver)
    # result = bestbuy_search("dyson", driver)
    # result = canadiantire_search("punching bag", driver, postalCode)
    # result = rona_search("dewalt drill", driver, postalCode)
    # result = homedepot_search("dewalt drill", driver, postalCode)
    result = staples_search("calculator", driver, postalCode)
    
    count = 1
    for r in result:
        print(f"{count}: {r['name']}, {r['price']}")
        count += 1
    driver.quit()  # quit only once at the end

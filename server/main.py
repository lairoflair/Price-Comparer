from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from scraper import bestbuy_search, canadiantire_search, staples_search, homedepot_search
import time
import asyncio
from typing import List, Dict, Any

# Import your scraper logic here
# from staples_scraper import staples_search
# http://127.0.0.1:8000/search?query=AA+battery&postal_code=M5V2T6

app = FastAPI()
executor = ThreadPoolExecutor(max_workers=3)

# Example Pydantic model for the product response
class Product(BaseModel):
    name: str
    price: str
    link: str



def run_scraper(scraper_func, query: str, postal_code: str):
    return scraper_func(query, postal_code)

async def run_with_retries(executor, scraper_func, query, postal_code, limit, max_retries=5):
    loop = asyncio.get_running_loop()
    last_exc = None

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt} → {scraper_func.__name__}")
            result = await loop.run_in_executor(executor, scraper_func, query, postal_code, limit)
            return result
        except Exception as e:
            print(f"{scraper_func.__name__} failed (attempt {attempt}): {e}")
            last_exc = e
            await asyncio.sleep(1)  # small backoff before retry

    # If all retries failed, raise the last exception
    raise last_exc

@app.get("/")
def root():
    return {"message": "API is running 🚀"}

@app.get("/search")
async def search_all(query: str, postal_code: str = "M5V2T6"):
    tasks = [
        run_with_retries(executor, bestbuy_search, query, postal_code, limit = 10),
        run_with_retries(executor, canadiantire_search, query, postal_code, limit = 5),
        run_with_retries(executor, staples_search, query, postal_code, limit = 5),
        run_with_retries(executor, homedepot_search, query, postal_code, limit = 5),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        "bestbuy": results[0],
        "canadiantire": results[1],
        "staples": results[2],
        "homedepot": results[3],
    }

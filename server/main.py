from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from scraper import bestbuy_search, canadiantire_search, staples_search, homedepot_search
import time
import asyncio
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Or specify ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    postal_code: str = "M5V2T6"
    bestbuy: bool = True
    canadiantire: bool = True
    staples: bool = True
    homedepot: bool = True
    
# Import your scraper logic here
# from staples_scraper import staples_search
# http://127.0.0.1:8000/search?query=AA+battery&postal_code=M5V2T6

executor = ThreadPoolExecutor(max_workers=4)

# Example Pydantic model for the product response
class Product(BaseModel):
    name: str
    price: str
    link: str
    image: Optional[str] = None

async def empty_result():
    return []

def run_scraper(scraper_func, query: str, postal_code: str):
    return scraper_func(query, postal_code)

async def run_with_retries(executor, scraper_func, query, postal_code, limit, max_retries=3):
    loop = asyncio.get_running_loop()
    last_exc = None

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt} → {scraper_func.__name__}")
            result = await loop.run_in_executor(executor, scraper_func, query, postal_code, limit)
            if result == []:
                print(f"{scraper_func.__name__} returned empty result (attempt {attempt})")
                last_exc = Exception("Empty result")
                await asyncio.sleep(1)  # small backoff before retry
                continue
            return result
        except Exception as e:
            print(f"{scraper_func.__name__} failed (attempt {attempt}): {e}")
            last_exc = e
            await asyncio.sleep(1)  # small backoff before retry

    # If all retries failed, raise the last exception
    return []
    # raise last_exc
    

@app.get("/")
def root():
    return {"message": "API is running 🚀"}

@app.get("/search")
async def search_all(query: str, postal_code: str = "M5V2T6", bestbuy: bool = True, canadiantire: bool = True, staples: bool = True, homedepot: bool = True):
    tasks = [
        run_with_retries(executor, bestbuy_search, query, postal_code, limit = 10),
        run_with_retries(executor, canadiantire_search, query, postal_code, limit = 10),
        run_with_retries(executor, staples_search, query, postal_code, limit = 10),
        run_with_retries(executor, homedepot_search, query, postal_code, limit = 10),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        "bestbuy": results[0],
        "canadiantire": results[1],
        "staples": results[2],
        "homedepot": results[3],
    }
    
@app.post("/search")
async def search_all(request: SearchRequest):
    tasks = []

    if request.bestbuy:
        tasks.append(run_with_retries(executor, bestbuy_search, request.query, request.postal_code, limit=10))
    else:
        tasks.append(empty_result())  # Placeholder for consistent indexing
        
    if request.canadiantire:
        tasks.append(run_with_retries(executor, canadiantire_search, request.query, request.postal_code, limit=5))
    else:
        tasks.append(empty_result())  # Placeholder for consistent indexing
        
    if request.staples:
        tasks.append(run_with_retries(executor, staples_search, request.query, request.postal_code, limit=5))
    else:
        tasks.append(empty_result())  # Placeholder for consistent indexing
        
    if request.homedepot:
        tasks.append(run_with_retries(executor, homedepot_search, request.query, request.postal_code, limit=5))
    else:
        tasks.append(empty_result())  # Placeholder for consistent indexing
        

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        "Best Buy": results[0] if request.bestbuy else [],
        "Canadian Tire": results[1] if request.canadiantire else [],
        "Staples": results[2] if request.staples else [],
        "Home Depot": results[3] if request.homedepot else [],
    }
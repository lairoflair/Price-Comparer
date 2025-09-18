import React, { useState } from 'react';

function App() {
    const [itemList, setItemList] = useState([]);
    const [bestBuy, setBestBuy] = useState(true);
    const [canadianTire, setCanadianTire] = useState(true);
    const [staples, setStaples] = useState(true);
    const [homeDepot, setHomeDepot] = useState(true);

    const findItem = async (item) => {
        try {
            const options = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: item,
                    postal_code: "M1B2K9",
                    bestbuy: bestBuy,
                    canadiantire: canadianTire,
                    staples: staples,
                    homedepot: homeDepot
                })
            };
            const result = await fetch('http://127.0.0.1:8000/search', options);
            const data = await result.json();
            console.log(data);
            setItemList(data);
        }catch (error) {
            console.error("Error fetching item data:", error);
        }
    }
  return (
    <>
        <div>
            <label>
                <input type="checkbox" checked={bestBuy} onChange={() => setBestBuy(!bestBuy)} />
                Best Buy
            </label>
            <label>
                <input type="checkbox" checked={canadianTire} onChange={() => setCanadianTire(!canadianTire)} />
                Canadian Tires
            </label>
            <label>
                <input type="checkbox" checked={staples} onChange={() => setStaples(!staples)} />
                Staples
            </label>
            <label>
                <input type="checkbox" checked={homeDepot} onChange={() => setHomeDepot(!homeDepot)} />
                Home Depot
            </label>
        </div>
        <div>
            <input id="SearchBar" type="text" placeholder="Search for a product..." />
            <input id="PostalCode" type="text" placeholder="Enter Postal Code..." />
            <button onClick={() => 
                findItem(document.querySelector('#SearchBar').value)}>Search
                </button>
        </div>
        <div>
            <h1>E-commerce Price Tracker</h1>
            <p>Track product prices from Amazon, Flipkart, and eBay.</p>
            {Object.entries(itemList).map(([storeName, items]) => (
            <div key={storeName} style={{ margin: '20px', border: '2px solid black', padding: '10px' }}>
                <h2>{storeName}</h2>
                <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                {items.map((item, index) => (
                    <div key={index} style={{ margin: '10px', border: '1px solid gray', padding: '10px' }}>
                    <h3>{item.name}</h3>
                    <p>Price: {item.price}</p>
                    <a href={item.link} target="_blank" rel="noopener noreferrer">
                        View Product
                    </a>
                    </div>
                ))}
                </div>
            </div>
            ))}
        </div>
    </>
  );
}

export default App;

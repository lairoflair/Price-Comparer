import React, { useState } from "react";
import "./App.css";
import "./Main Part.jsx";

function App() {
    const [searchItem, setSearchItem] = useState("");
    const [postalCode, setPostalCode] = useState("M5V2T6");
    const [itemList, setItemList] = useState({});
    const [bestBuy, setBestBuy] = useState(true);
    const [canadianTire, setCanadianTire] = useState(true);
    const [staples, setStaples] = useState(true);
    const [homeDepot, setHomeDepot] = useState(true);
    const [sortOption, setSortOption] = useState("price");

    const findItem = async () => {
        if (!searchItem || !postalCode) {
            alert("Please enter both a search item and a postal code.");
            return;
        }
        try {
            const options = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: searchItem,
                    postal_code: postalCode,
                    bestbuy: bestBuy,
                    canadiantire: canadianTire,
                    staples: staples,
                    homedepot: homeDepot,
                }),
            };
            const result = await fetch("http://127.0.0.1:8000/search", options);
            const data = await result.json();
            setItemList(data);
            console.log(data);
        } catch (error) {
            console.error("Error fetching item data:", error);
        }
    };

    // flatten all items if sorting by price
    const getSortedItems = () => {
        if (sortOption === "price") {
            const allItems = Object.entries(itemList)
                .flatMap(([store, items]) =>
                    items.map((item) => ({ ...item, store }))
                )
                .sort((a, b) => {
                    const priceA = parseFloat(a.price.replace(/[^0-9.-]+/g, ""));
                    const priceB = parseFloat(b.price.replace(/[^0-9.-]+/g, ""));
                    return priceA - priceB;
                });
            return allItems;
        }
        return itemList;
    };

    return (
        <div className="min-h-screen">
            {/* Top bar */}
            <div className="top-bar sticky top-0 z-10 bg-white shadow p-4 flex flex-col md:flex-row md:items-center md:justify-between">
                <div className="logo">E-commerce Price Comparer</div>
            </div>

            {/* Util bar */}
            <div>
                <div className="dropdowns">
                    {/* Stores dropdown */}
                    <div className="dropdown">
                        <button className="dropbtn">Stores</button>
                        <div className="dropdown-content">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={bestBuy}
                                    onChange={() => setBestBuy(!bestBuy)}
                                />
                                Best Buy
                            </label>
                            <label>
                                <input
                                    type="checkbox"
                                    checked={canadianTire}
                                    onChange={() => setCanadianTire(!canadianTire)}
                                />
                                Canadian Tire
                            </label>
                            <label>
                                <input
                                    type="checkbox"
                                    checked={staples}
                                    onChange={() => setStaples(!staples)}
                                />
                                Staples
                            </label>
                            <label>
                                <input
                                    type="checkbox"
                                    checked={homeDepot}
                                    onChange={() => setHomeDepot(!homeDepot)}
                                />
                                Home Depot
                            </label>
                        </div>
                    </div>

                    {/* Sort dropdown */}
                    <select
                        className="sort-select"
                        value={sortOption}
                        onChange={(e) => setSortOption(e.target.value)}
                    >
                        <option value="price">Sort by Price</option>
                        <option value="website">Sort by Website</option>
                    </select>
                </div>
            </div>
            {/* Search bar */}
            <div className="search-bar">
                <input
                    id="SearchBar"
                    type="text"
                    value={searchItem}
                    onChange={(e) => setSearchItem(e.target.value)}
                    placeholder="Search for a product..."
                />
                <input
                    id="PostalCode"
                    type="text"
                    value={postalCode}
                    onChange={(e) => setPostalCode(e.target.value)}
                    placeholder="Enter Postal Code..."
                />
                <button onClick={findItem}>Search</button>
            </div>

            {/* Main content */}
            <div className="flex min-h-screen">
                {/* Left Sidebar */}
                <div className="flex-[1] p-4">
                    <div className="sticky top-4 space-y-4"></div>
                </div>

                {/* Center */}
                <div className="flex-[8] p-4 max-w-screen-xl mx-auto">
                    {sortOption === "price" ? (
                        <div className="grid w-full grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                            {getSortedItems().map((item, index) => (
                                <div key={index} className="bg-white p-4 shadow rounded">
                                    <img
                                        src={item.image || "https://via.placeholder.com/150"}
                                        alt={item.name}
                                        className="w-full h-48 object-contain mb-2"
                                    />
                                    <h3 className="font-semibold">{item.name}</h3>
                                    <p>{item.price}</p>
                                    <p>{item.store}</p>
                                    <a
                                        href={item.link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className=" text-blue-500 underline mt-auto"
                                    >
                                        View Product
                                    </a>
                                </div>
                            ))}
                        </div>
                    ) : (
                        Object.entries(itemList).map(([storeName, items]) => (
                            items.length > 0 && (
                                <div key={storeName} className="mb-6">
                                    <div className="flex items-center gap-4 ">
                                        <h2 className="text-xl font-sans font-semibold tracking-wide uppercase mb-2 whitespace-nowrap">
                                            {storeName}
                                        </h2>
                                        <div className="overflow-x-auto w-full pt-2">
                                            <div className="flex gap-4 min-w-max">
                                                {items.map((item, index) => (
                                                    <div key={index} className="flex-shrink-0 w-60 bg-white p-4 shadow-md rounded">
                                                        <img
                                                            src={item.image || "https://via.placeholder.com/150"}
                                                            alt={item.name}
                                                            className="w-full h-40 object-contain mb-2"
                                                        />
                                                        <h3 className="font">{item.name}</h3>
                                                        <p>{item.price}</p>
                                                        <a
                                                            href={item.link}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="text-blue-500 underline"
                                                        >
                                                            View Product
                                                        </a>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )
                        ))
                    )}
                </div>

                {/* Right Sidebar */}
                <div className="flex-[1] p-4">
                    <div className="sticky top-4 space-y-4"></div>
                </div>
            </div>



        </div>
    );
}

export default App;

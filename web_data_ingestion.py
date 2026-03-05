import os
from datetime import datetime, timedelta

import yfinance as yf
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv(dotenv_path=".env")


def get_common_tickers() -> list[str]:
    """Return a small set of liquid, well‑known tickers."""
    return [
        "AAPL",   # Apple
        "MSFT",   # Microsoft
        "GOOGL",  # Alphabet
        "AMZN",   # Amazon
        "META",   # Meta Platforms
        "TSLA",   # Tesla
        "NVDA",   # NVIDIA
        "JPM",    # JPMorgan Chase
        "V",      # Visa
        "BRK-B",  # Berkshire Hathaway (B shares)
        "BTC-USD", # Bitcoin 
    ]


def fetch_stock_snapshot(ticker: str) -> dict:
    """
    Fetch a single snapshot of common stock information from yfinance.

    This keeps the schema small and predictable for use in the copilot.
    Uses get_info() to avoid the deprecated .info property.
    """
    t = yf.Ticker(ticker)
    info = t.get_info() or {}

    # Basic profile + key metrics
    snapshot = {
        "ticker": ticker,
        "shortName": info.get("shortName"),
        "longName": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),
        "currency": info.get("currency"),
        "marketCap": info.get("marketCap"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "beta": info.get("beta"),
        "dividendYield": info.get("dividendYield"),
        "trailingAnnualDividendRate": info.get("trailingAnnualDividendRate"),
        "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
        "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
        "fiftyDayAverage": info.get("fiftyDayAverage"),
        "twoHundredDayAverage": info.get("twoHundredDayAverage"),
        "averageVolume": info.get("averageVolume"),
        "enterpriseValue": info.get("enterpriseValue"),
        "profitMargins": info.get("profitMargins"),
        "operatingMargins": info.get("operatingMargins"),
        "returnOnEquity": info.get("returnOnEquity"),
        "returnOnAssets": info.get("returnOnAssets"),
        "totalRevenue": info.get("totalRevenue"),
        "grossMargins": info.get("grossMargins"),
        "ebitdaMargins": info.get("ebitdaMargins"),
        "currentPrice": info.get("currentPrice"),
        "previousClose": info.get("previousClose"),
        "open": info.get("open"),
        "dayHigh": info.get("dayHigh"),
        "dayLow": info.get("dayLow"),
        "volume": info.get("volume"),
        "sharesOutstanding": info.get("sharesOutstanding"),
        "pegRatio": info.get("pegRatio"),
        "priceToBook": info.get("priceToBook"),
        "epsTrailingTwelveMonths": info.get("epsTrailingTwelveMonths"),
        "epsForward": info.get("epsForward"),
        "recommendationKey": info.get("recommendationKey"),
        "website": info.get("website"),
        "logo_url": info.get("logo_url"),
        "asOf": datetime.utcnow(),
    }

    return snapshot


def fetch_recent_history(ticker: str, days: int = 90) -> list[dict]:
    """Fetch recent daily OHLCV data for the ticker."""
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    hist = yf.download(
        ticker,
        start=start.date().isoformat(),
        end=end.date().isoformat(),
        progress=False,
        auto_adjust=False,
    )

    records: list[dict] = []
    if hist is None or hist.empty:
        return records

    for index, row in hist.iterrows():
        records.append(
            {
                "ticker": ticker,
                "date": index.to_pydatetime(),
                "open": float(row.get("Open", 0.0)),
                "high": float(row.get("High", 0.0)),
                "low": float(row.get("Low", 0.0)),
                "close": float(row.get("Close", 0.0)),
                "adjClose": float(row.get("Adj Close", row.get("Close", 0.0))),
                "volume": int(row.get("Volume", 0)),
            }
        )
    return records


def ingest_to_mongo(
    connection_string: str,
    database_name: str = "stocks_database",
    snapshot_collection: str = "stocks",
    history_collection: str = "stocks_history",
) -> None:
    """
    Ingest snapshots and recent price history for a set of tickers into MongoDB.
    """
    client = MongoClient(connection_string)
    db = client[database_name]

    snapshots_col = db[snapshot_collection]
    history_col = db[history_collection]

    tickers = get_common_tickers()

    # Clear collections before re‑ingesting
    snapshots_col.delete_many({})
    history_col.delete_many({})

    snapshot_docs: list[dict] = []
    history_docs: list[dict] = []

    for symbol in tickers:
        snapshot_docs.append(fetch_stock_snapshot(symbol))
        history_docs.extend(fetch_recent_history(symbol))

    if snapshot_docs:
        snapshots_col.insert_many(snapshot_docs)
    if history_docs:
        history_col.insert_many(history_docs)

    client.close()


if __name__ == "__main__":
    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url:
        raise RuntimeError("MONGO_URL is not set in the environment/.env file.")

    ingest_to_mongo(mongo_url)


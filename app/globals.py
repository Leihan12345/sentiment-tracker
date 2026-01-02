# DEFINE GLOBALLY ACCESSIBLE CONSTANTS

from pathlib import Path
import re
import csv

BASE_DIR = Path(__file__).parent

SUPPORTED_SUBREDDITS = [
    "r/stocks",
    "r/StockMarket",
    "r/wallstreetbets",
    "r/options",
    "r/WallStreetbetsELITE",
    "r/Wallstreetbetsnew",
    "r/SPACs",
    "r/investing",
    "r/Daytrading",
    "r/pennystocks",
    "r/Shortsqueeze",
    "r/SqueezePlays"
]

# naiively keep all matches with our set of tickers
TICKER_PATTERN = re.compile(
    r'(?<![A-Za-z0-9])(?:\$[A-Za-z]{1,5}|[A-Z]{2,5})(?![A-Za-z0-9])'
)

COMMON_NON_TICKERS: set[str] = {
    "YOLO", "LOL", "LMAO", "ROFL", "WTF", "IDK", "IMO", "IMHO",
    "FYI", "BRB", "SMH", "TBH", "IRL", "TIL", "NSFW",

    "FOMO", "HODL", "TOS", "DD", "OTM", "ITM", "ATH", "CEO",
    "CFO", "CTO", "ETF", "IPO", "EPS", "PDT", "RR", "ATM", "AI",

    "DEC", "CPA", "DOT", "III", "AR", "DC", "AGI", "SG",

    "USA", "USD", "GDP", "FBI", "CIA", "SEC", "MD", "EU", "WB",
    "IP", "API", "BTC", "EOD", "TV", "RSI", "EMA", "PT", "CC",
    "FA", "IT", "BE", "OR", "ALL", "RH", "UK", "APP", "ES", "OP"
}

# set for O(1) access to tickers of the format: $XYZ
TICKER_SET = set()
with open("app/data/tickers_sec.csv") as tickers:
    reader = csv.reader(tickers)
    for row in reader:
        TICKER_SET.add(row[0])
# DEFINE GLOBALLY ACCESSIBLE CONSTANTS

from pathlib import Path
import re
import csv

BASE_DIR = Path(__file__).parent

SUPPORTED_SUBREDDITS = [
    "r/CryptoCurrency",
    "r/CryptoCurrencies",
    "r/Bitcoin",
    "r/SatoshiStreetBets",
    "r/CryptoMoonShots",
    "r/CryptoMarkets",
    "r/stocks",
    "r/wallstreetbets",
    "r/options",
    "r/WallStreetbetsELITE",
    "r/Wallstreetbetsnew",
    "r/SPACs",
    "r/investing",
    "r/Daytrading",
    "r/pennystocks"
]

# naiively keep all matches with our set of tickers
TICKER_PATTERN = re.compile(
    r'(?<![A-Za-z0-9$])'        # left boundary: not letter/digit/$
    r'\$[A-Z]{1,6}'             # $ required, 1–6 uppercase letters
    r'(?:\.[A-Z]{1,2})?'        # optional .class (e.g., $BRK.B)
    r'(?![A-Za-z0-9])'          # right boundary: not letter/digit
)


# set for O(1) access to tickers of the format: $XYZ
TICKER_SET = set()
with open("app/data/tickers.csv") as tickers:
    reader = csv.reader(tickers)
    for row in reader:
        TICKER_SET.add("$" + row[0])
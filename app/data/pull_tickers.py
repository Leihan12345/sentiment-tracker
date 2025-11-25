import pandas as pd

# to be run manually
def refresh_tickers():
    tickers = set()
    df = pd.read_csv("https://nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt", sep="|")
    tickers.update(df["Symbol"].dropna().tolist())
    with open("app/data/tickers.csv", "w") as f:
        for t in sorted(tickers):
            f.write(t + "\n")


if __name__ == "__main__":
    refresh_tickers()
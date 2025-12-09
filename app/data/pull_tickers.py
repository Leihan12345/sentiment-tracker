import json
import re
from pathlib import Path

# to be run manually
def refresh_tickers(json_path: Path = Path("app/data/sec_company_tickers.json"), out_path: Path = Path("app/data/tickers_sec.csv")):
    tickers = set()
    ticker_re = re.compile(r'^[A-Z0-9\.\-]{1,10}$')

    def collect(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                # direct ticker key
                if isinstance(k, str) and "ticker" in k.lower():
                    if isinstance(v, str):
                        val = v.strip().upper()
                        if ticker_re.match(val):
                            tickers.add(val)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, str):
                                val = item.strip().upper()
                                if ticker_re.match(val):
                                    tickers.add(val)
                    else:
                        collect(v)
                else:
                    # value itself might contain tickers deeper in structure
                    if isinstance(v, (dict, list)):
                        collect(v)
                    elif isinstance(v, str):
                        val = v.strip().upper()
                        if ticker_re.match(val):
                            tickers.add(val)
        elif isinstance(obj, list):
            for item in obj:
                collect(item)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON '{json_path}': {e}")
        return

    collect(data)

    # fallback: try pandas reading if nothing found or file is a flat table
    if not tickers:
        try:
            import pandas as pd

            df = pd.read_json(str(json_path))
            # SEC json columns are often: cik_str, ticker, title
            if "ticker" in df.columns:
                for t in df["ticker"].dropna().astype(str):
                    val = t.strip().upper()
                    if ticker_re.match(val):
                        tickers.add(val)
            else:
                # try any column containing 'ticker' in its name
                for col in df.columns:
                    if "ticker" in col.lower():
                        for t in df[col].dropna().astype(str):
                            val = t.strip().upper()
                            if ticker_re.match(val):
                                tickers.add(val)
        except Exception:
            # ignore pandas errors; we've already tried json traversal
            pass

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for t in sorted(tickers):
            f.write(t + "\n")

    print(f"Wrote {len(tickers)} tickers to {out_path}")


if __name__ == "__main__":
    refresh_tickers()

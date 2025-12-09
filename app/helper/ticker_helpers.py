from typing import Optional
from app.globals import TICKER_SET, TICKER_PATTERN, COMMON_NON_TICKERS

def extract_tickers(text: str) -> list[str]:
    candidates = TICKER_PATTERN.findall(text)
    filtered = []

    for ticker in candidates:
        if ticker[0] == "$":
            ticker = ticker.upper()
        else:
            if ticker in COMMON_NON_TICKERS:
                continue
        filtered.append(ticker)

    return filtered

def choose_main_ticker_post(title: str, body: str) -> Optional[str]:
    def valid_ticker(t: str) -> bool:
        return t in TICKER_SET or (t.startswith("$") and t[1:] in TICKER_SET)

    title_tickers = [t for t in extract_tickers(title) if valid_ticker(t)]
    body_tickers  = [t for t in extract_tickers(body)  if valid_ticker(t)]

    explicit_title = [t for t in title_tickers if t.startswith("$")]
    explicit_body  = [t for t in body_tickers  if t.startswith("$")]

    if explicit_title or explicit_body:
        title_tickers = explicit_title
        body_tickers  = explicit_body

    all_tickers = sorted(set(title_tickers + body_tickers))
    if not all_tickers:
        return None

    if len(title_tickers) == 1:
        return title_tickers[0]
    elif len(body_tickers) == 1:
        return body_tickers[0]

    from collections import Counter
    title_counts = Counter(title_tickers)
    body_counts  = Counter(body_tickers)

    if title_counts:
        most_common = title_counts.most_common()
        if len(most_common) == 1 or most_common[0][1] > most_common[1][1]:
            return most_common[0][0]

    scores: dict[str, int] = {}

    def leading_bonus(t: str, N: int = 15) -> int:
        idx = title.find(t)
        return 1 if 0 <= idx < N else 0

    for t in all_tickers:
        lead = leading_bonus(t)
        t_title = title_counts.get(t, 0)
        t_body  = body_counts.get(t, 0)
        score = 5 * lead + 3 * t_title + 1 * t_body
        scores[t] = score

    best = max(all_tickers, key=lambda t: scores[t])
    return best


def find_comment_tickers(body: str) -> set[str]:
    raw = extract_tickers(body)

    explicit: list[str] = []
    plain: list[str] = []

    for t in raw:
        if t.startswith("$"):
            if t[1:] in TICKER_SET:
                explicit.append(t)
        else:
            if t in TICKER_SET:
                plain.append(t)

    if explicit:
        return set(explicit)

    return set(plain)
    
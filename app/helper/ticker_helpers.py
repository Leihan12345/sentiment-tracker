from typing import Optional
from app.globals import TICKER_SET, TICKER_PATTERN

def extract_tickers(text: str) -> list[str]:
    candidates = TICKER_PATTERN.findall(text)
    return candidates

def choose_main_ticker(title: str, body: str) -> Optional[str]:
    title_tickers = [t for t in extract_tickers(title) if t in TICKER_SET]
    body_tickers  = [t for t in extract_tickers(body) if t in TICKER_SET]
    all_tickers   = sorted(set(title_tickers + body_tickers))

    if not all_tickers:
        return None

    # 1) low-hanging fruit; early exit
    if len(title_tickers) == 1:
        return title_tickers[0]
    elif len(body_tickers) == 1:
        return body_tickers[0]

    # 2) Count occurrences in title/body
    from collections import Counter
    title_counts = Counter(title_tickers)
    body_counts  = Counter(body_tickers)

    # If one ticker clearly dominates the title
    if title_counts:
        most_common = title_counts.most_common()
        if len(most_common) == 1 or most_common[0][1] > most_common[1][1]:
            return most_common[0][0]

    # 3) Full scoring
    scores = {}

    # helper: is ticker in the first N chars of title?
    def leading_bonus(t: str, N: int = 15) -> int:
        idx = title.find(t)
        return 1 if 0 <= idx < N else 0

    for t in all_tickers:
        lead = leading_bonus(t)
        t_title = title_counts.get(t, 0)
        t_body = body_counts.get(t, 0)

        score = (
            5 * lead +
            3 * t_title +
            1 * t_body
        )
        scores[t] = score

    best = max(all_tickers, key=lambda t: scores[t])

    return best

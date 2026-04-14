import feedparser
import re
from datetime import datetime
from database import get_connection

NASDAQ_FEED_URL = "https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts"


def remove_html(text):
    return re.sub("<.*?>", "", text or "")


def extract_halt_fields(summary_html):
    if not summary_html:
        return {}

    cells = re.findall(r"<td.*?>(.*?)</td>", summary_html)
    cells = [remove_html(c).strip() for c in cells]

    if len(cells) < 6:
        return {}

    return {
        "halt_date": cells[0],
        "halt_time": cells[1],
        "ticker": cells[2],
        "company": cells[3],
        "market": cells[4],
        "reason": cells[5],
    }


def save_to_database(halts):
    connection = get_connection()
    cursor = connection.cursor()

    for halt in halts:
        if not halt.get("ticker"):
            continue

        cursor.execute("""
            INSERT OR IGNORE INTO halts (
                ticker, company, reason,
                halt_time, halt_date, market, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            halt["ticker"],
            halt["company"],
            halt["reason"],
            halt["halt_time"],
            halt["halt_date"],
            halt["market"],
            halt["timestamp"]
        ))

    connection.commit()
    connection.close()


def fetch_and_store_halts():
    feed = feedparser.parse(NASDAQ_FEED_URL)

    results = []

    for entry in feed.entries:
        parsed = extract_halt_fields(entry.get("summary", ""))

        halt = {
            "ticker": parsed.get("ticker"),
            "company": parsed.get("company"),
            "reason": parsed.get("reason"),
            "halt_time": parsed.get("halt_time"),
            "halt_date": parsed.get("halt_date"),
            "market": parsed.get("market"),
            "timestamp": entry.get("published")
        }

        results.append(halt)

    save_to_database(results)
    return results


if __name__ == "__main__":
    data = fetch_and_store_halts()
    print(f"Saved {len(data)} halts")
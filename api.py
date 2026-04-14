from fastapi import FastAPI
import feedparser
import re
from datetime import datetime, timedelta

app = FastAPI()

NASDAQ_TRADE_HALT_FEED_URL = "https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts"


# ===== CLEAN HTML =====
def remove_html_tags(text):
    return re.sub("<.*?>", "", text or "")


# ===== EXTRACT STRUCTURED DATA =====
def extract_halt_fields(summary_html):
    if not summary_html:
        return {}

    table_cells = re.findall(r"<td.*?>(.*?)</td>", summary_html)
    table_cells = [remove_html_tags(cell).strip() for cell in table_cells]

    if len(table_cells) < 6:
        return {}

    return {
        "halt_date": table_cells[0],
        "halt_time": table_cells[1],
        "ticker": table_cells[2],
        "company": table_cells[3],
        "market": table_cells[4],
        "reason": table_cells[5],
    }


# ===== FETCH DATA FROM FEED =====
def fetch_halts():
    feed = feedparser.parse(NASDAQ_TRADE_HALT_FEED_URL)

    halt_results = []

    for entry in feed.entries:
        raw_summary_html = entry.get("summary", "")
        parsed_halt_data = extract_halt_fields(raw_summary_html)

        halt_results.append({
            "ticker": parsed_halt_data.get("ticker"),
            "company": parsed_halt_data.get("company"),
            "reason": parsed_halt_data.get("reason"),
            "halt_time": parsed_halt_data.get("halt_time"),
            "halt_date": parsed_halt_data.get("halt_date"),
            "market": parsed_halt_data.get("market"),
            "timestamp": entry.get("published")
        })

    return halt_results


# ===== API ROUTE =====
@app.get("/halts")
def get_halts(mode: str = "all"):
    halt_data = fetch_halts()

    if mode == "live":
        return halt_data[:10]

    if mode == "24h":
        cutoff_time = datetime.utcnow() - timedelta(days=1)
        filtered_halts = []

        for halt in halt_data:
            try:
                parsed_timestamp = datetime.strptime(
                    halt["timestamp"],
                    "%a, %d %b %Y %H:%M:%S %Z"
                )

                if parsed_timestamp >= cutoff_time:
                    filtered_halts.append(halt)

            except Exception:
                continue

        return filtered_halts

    return halt_data
import time
import feedparser
import re
from datetime import datetime, timedelta
from collections import deque

# ===== CONFIG =====
NASDAQ_FEED_URL = "https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts"

# stores only last 10 halts
recent_halts = deque(maxlen=10)

# used to prevent duplicates
seen_entries = set()

# ===== MODES =====
# 1 = LIVE ONLY (new since start)
# http://127.0.0.1:8000/halts?mode=live
# 2 = LAST 24 HOURS
# http://127.0.0.1:8000/halts?mode=24h
# 3 = FULL FEED
# http://127.0.0.1:8000/halts
current_mode = 1


# ===== CLEAN HTML =====
def remove_html_tags(text):
    if not text:
        return ""
    return re.sub("<.*?>", "", text)


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


# ===== PARSE TIME =====
def parse_timestamp(timestamp_string):
    try:
        return datetime.strptime(timestamp_string, "%a, %d %b %Y %H:%M:%S %Z")
    except:
        return None


# ===== FETCH HALTS =====
def fetch_halts():
    global seen_entries

    feed = feedparser.parse(NASDAQ_FEED_URL)

    # MODE 1: ignore all existing halts at startup
    if current_mode == 1 and not seen_entries:
        seen_entries = {
            entry.get("title", "") + entry.get("published", "")
            for entry in feed.entries
        }
        return

    cutoff_time = datetime.utcnow() - timedelta(days=1)

    for entry in feed.entries:
        unique_id = entry.get("title", "") + entry.get("published", "")

        if unique_id in seen_entries:
            continue

        seen_entries.add(unique_id)

        published_time = entry.get("published", "")
        parsed_time = parse_timestamp(published_time)

        # MODE 2: filter last 24 hours
        if current_mode == 2 and parsed_time and parsed_time < cutoff_time:
            continue

        parsed_fields = extract_halt_fields(entry.get("summary", ""))

        recent_halts.appendleft({
            "ticker": parsed_fields.get("ticker"),
            "company": parsed_fields.get("company"),
            "reason": parsed_fields.get("reason"),
            "halt_time": parsed_fields.get("halt_time"),
            "halt_date": parsed_fields.get("halt_date"),
            "market": parsed_fields.get("market"),
            "timestamp": published_time
        })


# ===== PRINT TERMINAL UI =====
def print_terminal_screen():
    print("\n" + "=" * 70)
    print("🚨 NASDAQ HALT MONITOR")
    print("=" * 70)

    print("\nMODES:")
    print("1 = LIVE (new since start)")
    print("2 = LAST 24 HOURS")
    print("3 = ALL DATA")
    print(f"➡️  CURRENT MODE: {current_mode}")

    print("\n" + "-" * 70)

    if not recent_halts:
        print("\nNo halts to display yet...\n")
        return

    for index, halt in enumerate(list(recent_halts), start=1):
        print(f"\n{index}. {halt['ticker']} ({halt['market']})")
        print(f"   🏢 Company: {halt['company']}")
        print(f"   ⚠️  Reason: {halt['reason']}")
        print(f"   ⏱ Halt Time: {halt['halt_time']} on {halt['halt_date']}")
        print(f"   📅 Published: {halt['timestamp']}")


# ===== HANDLE USER INPUT =====
def handle_user_input():
    global current_mode

    print("\nSwitch mode: [1] Live  [2] 24h  [3] All  |  [q] quit")
    user_input = input("> ").strip()

    if user_input in ["1", "2", "3"]:
        current_mode = int(user_input)
        recent_halts.clear()
        print("\n🔄 Mode changed — refreshing...\n")

    elif user_input.lower() == "q":
        print("Exiting...")
        exit()


# ===== MAIN LOOP =====
while True:
    fetch_halts()
    print_terminal_screen()
    handle_user_input()
    time.sleep(10)
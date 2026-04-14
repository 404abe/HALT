from fastapi import FastAPI
from database import get_connection, create_tables
from halt_scraper import fetch_and_store_halts
from datetime import datetime, timedelta

app = FastAPI()


@app.on_event("startup")
def startup():
    create_tables()


@app.get("/refresh")
def refresh_data():
    data = fetch_and_store_halts()
    return {"inserted": len(data)}


@app.get("/halts")
def get_halts(mode: str = "all"):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM halts ORDER BY id DESC")
    rows = cursor.fetchall()

    halts = [dict(row) for row in rows]

    if mode == "live":
        return halts[:10]

    if mode == "24h":
        cutoff = datetime.utcnow() - timedelta(days=1)

        filtered = []
        for h in halts:
            try:
                dt = datetime.strptime(h["timestamp"], "%a, %d %b %Y %H:%M:%S %Z")
                if dt >= cutoff:
                    filtered.append(h)
            except:
                continue

        return filtered

    return halts
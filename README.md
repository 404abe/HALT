# NASDAQ Halt Monitor

A real-time stock halt monitoring system built with Python and FastAPI.

## Features
- Fetches live halt data from Nasdaq RSS feed
- Parses structured data (ticker, company, reason)
- REST API with filtering (live / 24h / all)
- Terminal-based live monitor

## Tech Stack
- Python
- FastAPI
- feedparser

## Run Locally

### Start API
uvicorn api:app --reload

### Run Scraper
python3 halt_scraper.py

## Example Endpoint
/halts?mode=live
/halts?mode=24h
/halts


## Future Improvements
- Flutter mobile app (Trading212-style UI)
- Real-time alerts
- Notification system
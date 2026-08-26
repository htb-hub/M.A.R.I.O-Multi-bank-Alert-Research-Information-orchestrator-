import csv
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "results.db")
CSV_DIR = os.path.join(os.path.dirname(__file__), "data")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scrape_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scraped_at TEXT,
            source_type TEXT,
            name TEXT,
            url TEXT,
            info_type TEXT,
            title TEXT,
            link TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS security_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scraped_at TEXT,
            title TEXT,
            url TEXT,
            body TEXT
        )
    """)
    conn.commit()
    return conn


def save_scrape_results(results, source_type):
    conn = _get_conn()
    rows = []
    for r in results:
        name = r.get("name", "")
        url = r.get("url", "")
        scraped_at = r.get("scraped_at", datetime.now().isoformat())
        for item in r.get("failures", []):
            rows.append((scraped_at, source_type, name, url, "障害情報", item["title"], item["url"]))
        for item in r.get("releases", []):
            rows.append((scraped_at, source_type, name, url, "リリース情報", item["title"], item["url"]))
    conn.executemany(
        "INSERT INTO scrape_results (scraped_at, source_type, name, url, info_type, title, link) VALUES (?,?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    conn.close()
    _save_csv(rows, ["scraped_at", "source_type", "name", "url", "info_type", "title", "link"], "scrape_results")
    return rows


def save_security_news(articles):
    conn = _get_conn()
    rows = [(a.get("scraped_at", datetime.now().isoformat()), a.get("title", ""), a.get("url", ""), a.get("body", ""))
            for a in articles if "error" not in a]
    conn.executemany(
        "INSERT INTO security_news (scraped_at, title, url, body) VALUES (?,?,?,?)",
        rows
    )
    conn.commit()
    conn.close()
    _save_csv(rows, ["scraped_at", "title", "url", "body"], "security_news")
    return rows


def _save_csv(rows, headers, prefix):
    path = os.path.join(CSV_DIR, f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return path


def load_scrape_results():
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM scrape_results ORDER BY scraped_at DESC").fetchall()
    conn.close()
    return rows


def load_security_news():
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM security_news ORDER BY scraped_at DESC").fetchall()
    conn.close()
    return rows

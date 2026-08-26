import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

FAILURE_KEYWORDS = re.compile(r"障害|利用できない|ご利用いただけない")
RELEASE_KEYWORDS = re.compile(r"お知らせ|ニュース|リリース|アップデート|バージョン|機能追加|キャンペーン")

SECURITY_NEWS_URLS = [
    "https://www.security-next.com/date/{year}/{month:02d}"
]

def _get_soup(url):
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    text = res.text.replace("\r\r\n", "\n").replace("\r\n", "\n")
    return BeautifulSoup(text, "html.parser")


def _fetch_article_body(url):
    try:
        soup = _get_soup(url)
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        body = soup.find("article") or soup.find("main") or soup.find("body")
        return body.get_text(separator="\n", strip=True)[:2000] if body else ""
    except Exception:
        return ""


def _scrape_site(name, url, selector=None):
    results = {"name": name, "url": url, "failures": [], "releases": [], "scraped_at": datetime.now().isoformat()}
    try:
        soup = _get_soup(url)
        if selector:
            items = soup.select(selector)
            links = [(a.get_text(strip=True), a.get("href", "")) for item in items for a in item.find_all("a", href=True)]
        else:
            links = [(a.get_text(strip=True), a.get("href", "")) for a in soup.find_all("a", href=True)]

        for text, href in links:
            if not text:
                continue
            full_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
            if FAILURE_KEYWORDS.search(text):
                results["failures"].append({"title": text, "url": full_url})
            elif RELEASE_KEYWORDS.search(text):
                results["releases"].append({"title": text, "url": full_url})
    except Exception as e:
        results["error"] = str(e)
    return results


def scrape_from_list(sites):
    """sites: list of dict with keys name, url, selector(optional)"""
    return [_scrape_site(s["name"], s["url"], s.get("selector")) for s in sites]

#手入力
def scrape_from_url(url):
    return _scrape_site("手動入力", url)

#セキュリティニュース
def scrape_security_news():
    now = datetime.now()
    base_url = SECURITY_NEWS_URLS[0].format(year=now.year, month=now.month)
    results = []
    try:
        page = 1
        while True:
            url = base_url if page == 1 else f"{base_url}/page/{page}"
            soup = _get_soup(url)
            dts = soup.select("dl dt")
            if not dts:
                break
            for dt in dts:
                date_text = dt.get_text(strip=True)
                dd = dt.find_next_sibling("dd")
                if not dd:
                    continue
                a = dd.find("a", href=True)
                if not a:
                    continue
                title = a.get_text(strip=True)
                href = a["href"]
                body = _fetch_article_body(href)
                results.append({"date": date_text, "title": title, "url": href, "body": body, "scraped_at": now.isoformat()})
            next_link = soup.select_one("a.nextpostslink")
            if not next_link:
                break
            page += 1
    except Exception as e:
        results.append({"error": str(e)})
    return results

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
        body = soup.find("div", class_="content")
        if not body:
            return ""
        for tag in body.select("div.linkc, div.pnavi, div.sidebar"):
            tag.decompose()
        text = body.get_text(separator="\n", strip=True)
        # 関連リンク・PR・関連記事以降を切り捨て
        for marker in ["関連リンク", "関連記事", "PR", "ツイート"]:
            idx = text.find(marker)
            if idx != -1:
                text = text[:idx]
        return text.strip()[:2000]
    except Exception:
        return ""


def _scrape_site(name, url, selector=None, fetch_failures=True, fetch_releases=True):
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
            if fetch_failures and FAILURE_KEYWORDS.search(text):
                body = ""
                if full_url.lower().endswith(".pdf"):
                    body = "PDFをご確認お願いしますわ"
                else:
                    body = _fetch_article_body(full_url)
                results["failures"].append({"title": text, "url": full_url, "body": body})
            elif fetch_releases and RELEASE_KEYWORDS.search(text):
                results["releases"].append({"title": text, "url": full_url})
    except Exception as e:
        results["error"] = str(e)
    return results


def scrape_from_list(sites, fetch_failures=True, fetch_releases=True):
    """sites: list of dict with keys name, url, selector(optional)"""
    return [_scrape_site(s["name"], s["url"], s.get("selector"), fetch_failures=fetch_failures, fetch_releases=fetch_releases) for s in sites]

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
                if "脆弱性" in title:
                    continue
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

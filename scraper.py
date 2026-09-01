import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

FAILURE_KEYWORDS = re.compile(r"障害|利用できない|ご利用いただけない")
RELEASE_KEYWORDS = re.compile(r"お知らせ|ニュース|リリース|アップデート|バージョン|機能追加|キャンペーン")
LIST_URL_PATTERNS = re.compile(r"/(campaign|news|topics|information|release|notice|whatsnew|archive|list|category)s?/?$", re.IGNORECASE)

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
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        for tag in soup.select("ul.breadcrumb__list, ol.breadcrumb, nav.breadcrumb, .breadcrumb"):
            tag.decompose()
        body = soup.find("div", class_="content") or soup.find("main") or soup.find("article") or soup.find("body")
        if not body:
            return ""
        text = body.get_text(separator="\n", strip=True)
        for marker in ["関連リンク", "関連記事", "PR", "ツイート"]:
            idx = text.find(marker)
            if idx != -1:
                text = text[:idx]
        return text.strip()[:2000]
    except Exception:
        return ""


def _scrape_site(name, url, selector=None, fetch_failures=True, fetch_releases=True):
    results = {"name": name, "url": url, "failures": [], "releases": [], "scraped_at": datetime.now().isoformat()}
    seen_urls = set()
    try:
        soup = _get_soup(url)
        if selector:
            items = soup.select(selector)
            links = [(a.get_text(strip=True), a.get("href", "")) for item in items for a in item.find_all("a", href=True)]
        else:
            links = [(a.get_text(strip=True), a.get("href", "")) for a in soup.find_all("a", href=True)]

        LIST_PAGE_KEYWORDS = re.compile(r"一覧|トップ|ホーム|メニュー|サイトマップ|もっと見る|すべて見る|アーカイブ")
        for text, href in links:
            if not text or LIST_PAGE_KEYWORDS.search(text):
                continue
            full_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
            if full_url.rstrip("/") == url.rstrip("/") or LIST_URL_PATTERNS.search(full_url):
                continue
            if fetch_failures and FAILURE_KEYWORDS.search(text) and full_url not in seen_urls:
                seen_urls.add(full_url)
                body = "PDFをご確認お願いしますわ" if full_url.lower().endswith(".pdf") else _fetch_article_body(full_url)
                results["failures"].append({"title": text, "url": full_url, "body": body})
            elif fetch_releases and RELEASE_KEYWORDS.search(text) and full_url not in seen_urls:
                seen_urls.add(full_url)
                results["releases"].append({"title": text, "url": full_url})
    except Exception as e:
        results["error"] = str(e)
    return results


def scrape_from_list(sites, fetch_failures=True, fetch_releases=True):
    """sites: list of dict with keys name, url, selector(optional)"""
    seen = set()
    unique_sites = []
    for s in sites:
        if s["url"] not in seen:
            seen.add(s["url"])
            unique_sites.append(s)
    return [_scrape_site(s["name"], s["url"], s.get("selector"), fetch_failures=fetch_failures, fetch_releases=fetch_releases) for s in unique_sites]

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

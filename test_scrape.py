import requests, re
from bs4 import BeautifulSoup

HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
FAILURE_KEYWORDS = re.compile(r'障害|利用できない|ご利用いただけない')

res = requests.get('https://www.fukuibank.co.jp', headers=HEADERS, timeout=10)
res.encoding = res.apparent_encoding
soup = BeautifulSoup(res.text, 'html.parser')
links = [(a.get_text(strip=True), a.get('href','')) for a in soup.find_all('a', href=True)]
failures = [(t,h) for t,h in links if t and FAILURE_KEYWORDS.search(t)]
print('failures:', failures[:5])

if failures:
    href = failures[0][1]
    url = href if href.startswith('http') else 'https://www.fukuibank.co.jp/' + href.lstrip('/')
    print('link url:', url)
    res2 = requests.get(url, headers=HEADERS, timeout=10)
    res2.encoding = res2.apparent_encoding
    soup2 = BeautifulSoup(res2.text, 'html.parser')
    classes = [t.name+' '+' '.join(t.get('class',[])) for t in soup2.find_all(True) if t.get('class')]
    print('\n'.join(classes[:30]))
    print('---body text---')
    body = soup2.find('main') or soup2.find('article') or soup2.find('body')
    print(body.get_text(separator='\n', strip=True)[:500] if body else 'NOT FOUND')

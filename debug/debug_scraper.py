import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
res = requests.get('https://www.security-next.com/date/2026/08', headers=HEADERS, timeout=10)
res.encoding = res.apparent_encoding
text = res.text.replace('\r\r\n', '\n').replace('\r\n', '\n')
soup = BeautifulSoup(text, 'html.parser')

dts = soup.select('dl dt')
dls = soup.find_all('dl')

with open('debug_result.txt', 'w', encoding='utf-8') as f:
    f.write(f"dl count: {len(dls)}\n")
    f.write(f"dl dt count: {len(dts)}\n")
    if dls:
        f.write("--- first dl prettify ---\n")
        f.write(dls[0].prettify()[:2000])
    if dts:
        f.write("\n--- first dt ---\n")
        f.write(str(dts[0]))
        dd = dts[0].find_next_sibling('dd')
        f.write(f"\n--- next sibling dd ---\n{dd}\n")

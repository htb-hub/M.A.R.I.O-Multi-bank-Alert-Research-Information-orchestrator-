from scraper import scrape_security_news
results = scrape_security_news()
with open('debug_result2.txt', 'w', encoding='utf-8') as f:
    f.write(f"count: {len(results)}\n")
    for r in results[:3]:
        f.write(str(r) + '\n')

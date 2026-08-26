import streamlit as st
import openpyxl
import os
from scraper import scrape_from_list, scrape_from_url, scrape_security_news
from storage import save_scrape_results, save_security_news, load_scrape_results, load_security_news
from notifier import send_mail, send_slack

NEWSLIST_PATH = os.path.join(os.path.dirname(__file__), "Newslist.xlsx")


def load_newslist():
    wb = openpyxl.load_workbook(NEWSLIST_PATH)
    ws = wb.active
    sites = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        name, url, selector = (list(row) + [None, None, None])[:3]
        if name and url:
            sites.append({"name": name, "url": url, "selector": selector})
    return sites


def display_results(results):
    for r in results:
        if "error" in r:
            st.error(f"{r.get('name', '')} : {r['error']}")
            continue
        failures = r.get("failures", [])
        releases = r.get("releases", [])
        if not failures and not releases:
            continue
        with st.expander(f"📌 {r['name']} ({r['url']})"):
            if failures:
                st.markdown("**🔴 障害情報**")
                for item in failures:
                    st.markdown(f"- [{item['title']}]({item['url']})")
            if releases:
                st.markdown("**🟢 リリース情報**")
                for item in releases:
                    st.markdown(f"- [{item['title']}]({item['url']})")


def notify_and_save(results, source_type):
    saved = save_scrape_results(results, source_type)
    st.success(f"{len(saved)} 件を保存しましたわ")
    ok, msg = send_mail(results, source_type)
    st.info(f"メール: {msg}")
    ok2, msg2 = send_slack(results, source_type)
    if ok2:
        st.info(f"Slack: {msg2}")


st.set_page_config(page_title="情報収集アプリ", layout="wide")
st.title("📰 情報収集・通知アプリ")

tab1, tab2, tab3 = st.tabs(["📋 固定リスト", "🔒 セキュリティニュース", "🔗 URL直打ち"])

# ── タブ1: 固定リスト ──
with tab1:
    st.subheader("固定リストからスクレイピング")
    sites = load_newslist()
    st.write(f"対象サイト数: {len(sites)} 件")
    if st.button("実行", key="run_list"):
        with st.spinner("スクレイピング中ですわ..."):
            results = scrape_from_list(sites)
        display_results(results)
        notify_and_save(results, "固定リスト")

    st.divider()
    st.subheader("過去の収集結果")
    rows = load_scrape_results()
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows, columns=["id", "scraped_at", "source_type", "name", "url", "info_type", "title", "link"])
        st.dataframe(df[df["source_type"] == "固定リスト"].drop(columns=["id"]), use_container_width=True)

# ── タブ2: セキュリティニュース ──
with tab2:
    st.subheader("security-next.com 今月のニュース")
    if st.button("実行", key="run_news"):
        with st.spinner("取得中ですわ..."):
            articles = scrape_security_news()
        st.session_state["security_articles"] = articles

    articles = st.session_state.get("security_articles", [])
    if not articles:
        st.info("実行ボタンを押して取得してくださいませ")
    elif "error" in articles[0]:
        st.error(articles[0].get("error", "取得失敗"))
    else:
        st.success(f"{len(articles)} 件取得しましたわ")
        for a in articles:
            with st.expander(f"{a.get('date', '')}　{a['title']}"):
                st.markdown(f"[記事リンク]({a['url']})")
                st.text(a.get("body", ""))
        if st.button("保存", key="save_news"):
            save_security_news(articles)
            st.success(f"{len(articles)} 件を保存しましたわ")

    st.divider()
    st.subheader("過去の収集結果")
    news_rows = load_security_news()
    if news_rows:
        import pandas as pd
        df_news = pd.DataFrame(news_rows, columns=["id", "scraped_at", "title", "url", "body"])
        st.dataframe(df_news.drop(columns=["id", "body"]), use_container_width=True)

# ── タブ3: URL直打ち ──
with tab3:
    st.subheader("URLを直接入力してスクレイピング")
    url_input = st.text_input("URL", placeholder="https://example.com")
    if st.button("実行", key="run_url") and url_input:
        with st.spinner("スクレイピング中ですわ..."):
            result = scrape_from_url(url_input)
        display_results([result])
        notify_and_save([result], "URL直打ち")

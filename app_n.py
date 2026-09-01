import streamlit as st
import openpyxl
import os
import random
import time
import pandas as pd
from scraper import scrape_from_list, scrape_security_news
from storage import save_scrape_results, save_security_news, load_scrape_results, load_security_news
from notifier import send_mail, send_slack

NEWSLIST_PATH = os.path.join(os.path.dirname(__file__), "Newslist.xlsx")

DEPARTMENTS = ["―部署を選択―", "指定しない", "デジバン（NCBアプリ）","営業企画部", "総合企画部", "法人ソリューション部", "事務統括部"]

TIPS = [
    "HTTPステータスコード『418』は『I'm a teapot』。エイプリルフールで作られたジョーク規格ですわ。",
    "スクレイピング時は `robots.txt` の確認と適切なリクエスト間隔（sleep）を設定するのがマナーですわね。",
    "最初のコンピュータバグは、本当に本物の「蛾」がリレーに挟まったことが由来と言われていますの。",
    "User-Agentを適切に設定しておくと、相手サーバーにも優しく接してもらえますわよ。",
    "Pythonの名称は蛇ではなく、イギリスのコメディ番組『空飛ぶモンティ・パイソン』が由来ですの。",
    "正規表現でHTMLをパースしようとすると沼にハマりますわ。素直にBeautifulSoupなどを使いましょう。",
    "JavaScriptは1995年にわずか10日間で開発された言語ですのよ。",
    "エラーが出たときは、まず「全角スペース」と「タイポ」を疑うのが解決への近道ですわ。",
    "データ取得完了まであと少し！温かい紅茶でも飲んで優雅にお待ちになってはいかがかしら？",
]


def load_newslist():
    wb = openpyxl.load_workbook(NEWSLIST_PATH)
    ws = wb.active
    sites = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        name, url, selector = (list(row) + [None, None, None])[:3]
        if name and url:
            sites.append({"name": name, "url": url, "selector": selector})
    return sites


def display_by_name(results, key):
    by_name = {}
    for r in results:
        if "error" in r:
            st.error(f"{r.get('name', '')} : {r['error']}")
            continue
        for item in r.get(key, []):
            by_name.setdefault(r["name"], []).append(item)
    if not by_name:
        st.info("該当する情報はありませんでした")
        return
    for name, items in by_name.items():
        with st.expander(f"📌 {name}"):
            for item in items:
                st.markdown(f"- [{item['title']}]({item['url']})")
                if item.get("body"):
                    st.text(item["body"])


def notify_and_save(results, source_type):
    saved = save_scrape_results(results, source_type)
    st.success(f"{len(saved)} 件を保存しましたわ")
    ok, msg = send_mail(results, source_type)
    st.info(f"メール: {msg}")
    ok2, msg2 = send_slack(results, source_type)
    if ok2:
        st.info(f"Slack: {msg2}")


st.set_page_config(page_title="M.A.R.I.O", layout="wide")
st.title("M.A.R.I.O")
st.caption("-Multibank Alert Research Information Orchestrator-")

with st.chat_message("mario", avatar="img/character.png"):
    st.markdown("他行の最新情報や障害の発生状況の調査や、セキュリティニュースが確認できますわ。")
    st.markdown("CSV保存、メール送信ももちろん可能ですわよ")

with st.sidebar:
    if st.button("収集結果をリセット"):
        for key in ["results_releases", "results_failures", "security_articles"]:
            st.session_state.pop(key, None)
        st.success("リセットしましたわ")


tab1, tab2, tab3 = st.tabs(["🟢 他行最新情報", "🔴 障害情報", "🔒 セキュリティニュース"])

# ── タブ1: リリース情報 ──
with tab1:
    st.subheader("他行最新情報")
    sites = load_newslist()
    st.write(f"対象サイト数: {len(sites)} 件")
    selected_dept = st.selectbox("部署を選択", DEPARTMENTS, key="dept_releases")
    if st.button("実行", key="run_releases"):
        if selected_dept == "―部署を選択―":
            st.warning("部署を選択してくださいませ")
        else:
            st.session_state["selected_dept"] = selected_dept
            tip_box = st.empty()
            tip_box.info(f"💡 **Tips**: {random.choice(TIPS)}")
            st.markdown("待ってる間に[診断をどうぞ](https://prismatic-palmier-3d328b.netlify.app/index.html)")
            st.markdown("お待ちの間、横のメニューからお勉強できますわよ。")
            with st.spinner("スクレイピング中ですわ..."):
                results = scrape_from_list(sites, fetch_failures=False, fetch_releases=True)
            tip_box.empty()
            st.session_state["results_releases"] = results
            notify_and_save(results, "リリース情報")

    results = st.session_state.get("results_releases", [])
    if results:
        all_items = [{"name": r["name"], "title": item["title"], "url": item["url"]} for r in results if "error" not in r for item in r.get("releases", [])]
        if all_items:
            df_rel = pd.DataFrame(all_items)
            st.download_button("CSVダウンロード", df_rel.to_csv(index=False).encode("utf-8-sig"), "releases.csv", "text/csv")
        display_by_name(results, "releases")

    st.divider()
    st.subheader("過去の収集結果")
    rows = load_scrape_results()
    if rows:
        df = pd.DataFrame(rows, columns=["id", "scraped_at", "source_type", "name", "url", "info_type", "title", "link"])
        st.dataframe(df[df["source_type"] == "リリース情報"].drop(columns=["id"]), use_container_width=True)

# ── タブ2: 障害情報 ──
with tab2:
    st.subheader("障害情報")
    sites = load_newslist()
    st.write(f"対象サイト数: {len(sites)} 件")
    if st.button("実行", key="run_failures"):
        tip_box = st.empty()
        tip_box.info(f"💡 **Tips**: {random.choice(TIPS)}")
        st.markdown("待ってる間に[診断をどうぞ](https://prismatic-palmier-3d328b.netlify.app/index.html)")
        st.markdown("お待ちの間、横のメニューからお勉強できますわよ。")
        with st.spinner("スクレイピング中ですわ..."):
            results = scrape_from_list(sites, fetch_failures=True, fetch_releases=False)
        tip_box.empty()
        st.session_state["results_failures"] = results
        notify_and_save(results, "障害情報")

    results = st.session_state.get("results_failures", [])
    if results:
        display_by_name(results, "failures")

    st.divider()
    st.subheader("過去の収集結果")
    rows = load_scrape_results()
    if rows:
        df = pd.DataFrame(rows, columns=["id", "scraped_at", "source_type", "name", "url", "info_type", "title", "link"])
        st.dataframe(df[df["source_type"] == "障害情報"].drop(columns=["id"]), use_container_width=True)

# ── タブ3: セキュリティニュース ──
with tab3:
    st.subheader("security-next.com 今月のニュース")
    if st.button("実行", key="run_news"):
        tip_box = st.empty()
        tip_box.info(f"💡 **Tips**: {random.choice(TIPS)}")
        st.markdown("待ってる間に[診断をどうぞ](https://prismatic-palmier-3d328b.netlify.app/index.html)")
        st.markdown("お待ちの間、横のメニューからお勉強できますわよ。")
        with st.spinner("取得中ですわ..."):
            articles = scrape_security_news()
        tip_box.empty()
        st.session_state["security_articles"] = articles

    articles = st.session_state.get("security_articles", [])
    if not articles:
        st.info("実行ボタンを押して取得してくださいませ")
    elif "error" in articles[0]:
        st.error(articles[0].get("error", "取得失敗"))
    else:
        st.success(f"{len(articles)} 件取得しましたわ")
        df_articles = pd.DataFrame(articles, columns=["date", "title", "url", "body"])
        st.download_button("CSVダウンロード", df_articles.to_csv(index=False).encode("utf-8-sig"), "security_news.csv", "text/csv")
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
        df_news = pd.DataFrame(news_rows, columns=["id", "scraped_at", "title", "url", "body"])
        st.dataframe(df_news.drop(columns=["id", "body"]), use_container_width=True)

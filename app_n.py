import streamlit as st
import openpyxl
import os
<<<<<<< HEAD
import random
=======
>>>>>>> 22c9db31020a2f3d90eb75ce67157052ed33b597
import time
import pandas as pd
from scraper import scrape_from_list, scrape_security_news
from storage import save_scrape_results, save_security_news, load_scrape_results, load_security_news
from notifier import send_mail, send_slack

NEWSLIST_PATH = os.path.join(os.path.dirname(__file__), "Newslist.xlsx")
GLOSSARY_PATH = os.path.join(os.path.dirname(__file__), "デジタルサービス企画_システム用語集.csv")


@st.cache_data
def load_glossary():
    df = pd.read_csv(GLOSSARY_PATH, encoding="utf-8-sig")
    return df.to_dict("records")


def init_glossary_index():
    from datetime import date
    today_key = f"glossary_date_{date.today().isoformat()}"
    if today_key not in st.session_state:
        glossary = load_glossary()
        st.session_state["glossary_index"] = hash(date.today().isoformat()) % len(glossary)
        st.session_state[today_key] = True


def show_glossary_widget(key_suffix=""):
    glossary = load_glossary()
    init_glossary_index()
    elapsed_steps = int(time.time() // 30)
    idx = (st.session_state["glossary_index"] + elapsed_steps) % len(glossary)
    item = glossary[idx]
    with st.container(border=True):
        st.markdown(f"📖 **{item['用語']}**：{item['解説']}")

# デフゾーン
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

# Tips
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


# サイトコンフィグ
st.set_page_config(page_title="M.A.R.I.O", layout="wide")
st.title("M.A.R.I.O")
st.caption("-Multibank Alert Research Information Orchestrator-")

with st.chat_message("mario", avatar="img/character.png"):
    st.markdown("他行の最新情報情報や障害の発生状況の調査や、セキュリティニュースが確認できますわ。")
    st.markdown("CSV保存、メール送信ももちろん可能ですわよ")

DEPARTMENTS = ["―部署を選択―", "営業企画部", "総合企画部", "法人ソリューション部", "事務統括部"]

tab1, tab2, tab3 = st.tabs(["🟢 他行最新情報", "🔴 障害情報", "🔒 セキュリティニュース"])

# ── タブ1: リリース情報 ──
with tab1:
    st.subheader("他行最新情報")
    sites = load_newslist()
    st.write(f"対象サイト数: {len(sites)} 件")
<<<<<<< HEAD
    if st.button("実行", key="run_releases"):
        # 初回表示
        current_tip = random.choice(TIPS)
        tip_box = st.empty()  # 1箇所だけ書き換える領域を作成
        last_tip_time = 0
        tip_interval = 6  # 6秒ごとにTipsを変更
        tip_box.info(f"💡 **Tips**: {current_tip}")

=======
    show_glossary_widget("tab1")
    col_btn1, col_dept1, col_rest1 = st.columns([1, 2, 5])
    with col_btn1:
        st.markdown("<div style='padding-top:28px'>", unsafe_allow_html=True)
        run_releases = st.button("実行", key="run_releases")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_dept1:
        st.markdown("<div style='padding-left:15px;padding-top:28px'>", unsafe_allow_html=True)
        st.selectbox("", DEPARTMENTS, key="dept_releases", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    if run_releases:
>>>>>>> 22c9db31020a2f3d90eb75ce67157052ed33b597
        with st.spinner("スクレイピング中ですわ..."):
            if time.time() - last_tip_time > tip_interval:
                current_tip = random.choice(TIPS)
                tip_box.info(f"💡 **Tips**: {current_tip}")
                last_tip_time = time.time()
            st.markdown("待ってる間に[診断をどうぞ](https://prismatic-palmier-3d328b.netlify.app/index.html)")
            results = scrape_from_list(sites, fetch_failures=False, fetch_releases=True)
        st.session_state["results_releases"] = results
        notify_and_save(results, "リリース情報")

    results = st.session_state.get("results_releases", [])
    if results:
        tip_box.empty()  # 終わったらTips枠を消去
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
<<<<<<< HEAD
    if st.button("実行", key="run_failures"):
        # 初回表示
        current_tip = random.choice(TIPS)
        tip_box = st.empty()  # 1箇所だけ書き換える領域を作成
        last_tip_time = 0
        tip_interval = 6  # 6秒ごとにTipsを変更
        tip_box.info(f"💡 **Tips**: {current_tip}")
=======
    show_glossary_widget("tab2")
    col_btn2, col_dept2, col_rest2 = st.columns([1, 2, 5])
    with col_btn2:
        st.markdown("<div style='padding-top:28px'>", unsafe_allow_html=True)
        run_failures = st.button("実行", key="run_failures")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_dept2:
        st.markdown("<div style='padding-left:15px;padding-top:28px'>", unsafe_allow_html=True)
        st.selectbox("", DEPARTMENTS, key="dept_failures", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    if run_failures:
>>>>>>> 22c9db31020a2f3d90eb75ce67157052ed33b597
        with st.spinner("スクレイピング中ですわ..."):
            if time.time() - last_tip_time > tip_interval:
                current_tip = random.choice(TIPS)
                tip_box.info(f"💡 **Tips**: {current_tip}")
                last_tip_time = time.time()
            st.markdown("待ってる間に[診断をどうぞ](https://prismatic-palmier-3d328b.netlify.app/index.html)")
            results = scrape_from_list(sites, fetch_failures=True, fetch_releases=False)
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
<<<<<<< HEAD
    if st.button("実行", key="run_news"):
                # 初回表示
        current_tip = random.choice(TIPS)
        tip_box = st.empty()  # 1箇所だけ書き換える領域を作成
        last_tip_time = 0
        tip_interval = 6  # 6秒ごとにTipsを変更
        tip_box.info(f"💡 **Tips**: {current_tip}")
=======
    show_glossary_widget("tab3")
    col_btn3, col_dept3, col_rest3 = st.columns([1, 2, 5])
    with col_btn3:
        st.markdown("<div style='padding-top:28px'>", unsafe_allow_html=True)
        run_news = st.button("実行", key="run_news")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_dept3:
        st.markdown("<div style='padding-left:15px;padding-top:28px'>", unsafe_allow_html=True)
        st.selectbox("", DEPARTMENTS, key="dept_news", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    if run_news:
>>>>>>> 22c9db31020a2f3d90eb75ce67157052ed33b597
        with st.spinner("取得中ですわ..."):
            
            st.markdown("待ってる間に[診断をどうぞ](https://prismatic-palmier-3d328b.netlify.app/index.html)")
            articles = scrape_security_news()
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

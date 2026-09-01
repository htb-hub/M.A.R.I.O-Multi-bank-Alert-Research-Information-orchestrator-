import streamlit as st
import pandas as pd
import os
import random

GLOSSARY_PATH = os.path.join(os.path.dirname(__file__), "デジタルサービス企画_システム用語集.csv")
TOTAL = 10

st.set_page_config(page_title="用語クイズ", layout="centered")
st.title("📖 システム用語クイズ")
st.caption("用語の解説として正しいものを選んでください")


@st.cache_data
def load_glossary():
    df = pd.read_csv(GLOSSARY_PATH, encoding="utf-8-sig")
    return df.to_dict("records")


glossary = load_glossary()


def start_quiz():
    questions = []
    for correct in random.sample(glossary, TOTAL):
        wrongs = random.sample([g for g in glossary if g["用語"] != correct["用語"]], 3)
        choices = [correct["解説"]] + [g["解説"] for g in wrongs]
        random.shuffle(choices)
        questions.append({
            "term": correct["用語"],
            "category": correct["カテゴリ"],
            "answer": correct["解説"],
            "choices": choices,
        })
    st.session_state["questions"] = questions
    st.session_state["current"] = 0
    st.session_state["score"] = 0
    st.session_state["q_result"] = None
    st.session_state["finished"] = False


if "questions" not in st.session_state:
    start_quiz()

if st.session_state["finished"]:
    st.subheader(f"🎉 クイズ終了！")
    st.metric("スコア", f"{st.session_state['score']} / {TOTAL}")
    score = st.session_state['score']
    if score == 0:
        st.error("幼稚園からやり直してこい")
    elif score <= 3:
        st.warning("少々お勉強が必要ですわね、、、")
    elif score <= 7:
        st.info("なかなかですわ！基本はばっちりですわね！")
    elif score <= 9:
        st.success("流石でございますわ！！")
    else:
        st.success("カワバンガ！！")
    if st.button("もう一度", type="primary"):
        start_quiz()
        st.rerun()
else:
    idx = st.session_state["current"]
    q = st.session_state["questions"][idx]

    st.progress((idx) / TOTAL, text=f"{idx + 1} / {TOTAL} 問目")
    st.markdown(f"**カテゴリ：{q['category']}**")
    st.subheader(f"「{q['term']}」の解説はどれ？")
    st.divider()

    for i, choice in enumerate(q["choices"]):
        if st.button(choice, key=f"choice_{i}", use_container_width=True, disabled=st.session_state["q_result"] is not None):
            st.session_state["q_result"] = (choice == q["answer"])
            if st.session_state["q_result"]:
                st.session_state["score"] += 1

    if st.session_state["q_result"] is True:
        st.success("✅ 正解！")
    elif st.session_state["q_result"] is False:
        st.error(f"❌ 不正解… 正解は：\n\n{q['answer']}")

    if st.session_state["q_result"] is not None:
        is_last = (idx + 1 == TOTAL)
        label = "結果を見る 🏁" if is_last else "次の問題 ▶"
        if st.button(label, type="primary"):
            st.session_state["current"] += 1
            st.session_state["q_result"] = None
            if is_last:
                st.session_state["finished"] = True
            st.rerun()

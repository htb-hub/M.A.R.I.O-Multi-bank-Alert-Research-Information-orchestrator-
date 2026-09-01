import streamlit as st
import pandas as pd
import os
import random

GLOSSARY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "デジタルサービス企画_システム用語集.csv"))

st.set_page_config(page_title="用語クイズ", layout="centered")
st.title("📖 システム用語クイズ")
st.caption("用語の解説として正しいものを選んでください")


@st.cache_data
def load_glossary():
    df = pd.read_csv(GLOSSARY_PATH, encoding="utf-8-sig")
    return df.to_dict("records")


glossary = load_glossary()


def new_question():
    correct = random.choice(glossary)
    wrongs = random.sample([g for g in glossary if g["用語"] != correct["用語"]], 3)
    choices = [correct["解説"]] + [g["解説"] for g in wrongs]
    random.shuffle(choices)
    st.session_state["q_term"] = correct["用語"]
    st.session_state["q_category"] = correct["カテゴリ"]
    st.session_state["q_answer"] = correct["解説"]
    st.session_state["q_choices"] = choices
    st.session_state["q_result"] = None
    st.session_state["q_selected"] = None


if "q_term" not in st.session_state:
    new_question()

st.markdown(f"**カテゴリ：{st.session_state['q_category']}**")
st.subheader(f"「{st.session_state['q_term']}」の解説はどれ？")
st.divider()

for i, choice in enumerate(st.session_state["q_choices"]):
    if st.button(choice, key=f"choice_{i}", use_container_width=True):
        st.session_state["q_selected"] = choice
        st.session_state["q_result"] = (choice == st.session_state["q_answer"])

if st.session_state.get("q_result") is True:
    st.success("✅ 正解！")
elif st.session_state.get("q_result") is False:
    st.error(f"❌ 不正解… 正解は：\n\n{st.session_state['q_answer']}")

if st.session_state.get("q_result") is not None:
    if st.button("次の問題 ▶", type="primary"):
        new_question()
        st.rerun()

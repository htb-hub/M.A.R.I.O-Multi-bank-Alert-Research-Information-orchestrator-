import streamlit as st
import pandas as pd
import os
import random

GLOSSARY_PATH = os.path.join(os.path.dirname(__file__), "glossary.csv")
st.set_page_config(page_title="ITPASSTA", layout="centered")
st.title("IT.PASSTA🍝")
st.caption("用語の解説として正しいものを選んでください")


@st.cache_data
def load_glossary():
    df = pd.read_csv(GLOSSARY_PATH, encoding="utf-8-sig")
    return df.to_dict("records")


glossary = load_glossary()


def start_quiz():
    total = st.session_state.get("total", 10)
    pool = st.session_state.get("pool", glossary)
    questions = []
    for correct in random.sample(pool, total):
        wrongs = random.sample([g for g in pool if g["用語"] != correct["用語"]], min(3, len(pool) - 1))
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
    st.session_state["wrong_answers"] = []


if "questions" not in st.session_state:
    total = st.selectbox("設問数を選んでください", options=list(range(10, 110, 10)), index=0)
    st.markdown("**出題カテゴリを選んでください**")
    all_categories = sorted({g["カテゴリ"] for g in glossary})
    cols = st.columns(3)
    selected = {cat: cols[i % 3].checkbox(cat, value=True) for i, cat in enumerate(all_categories)}
    enabled = [cat for cat, on in selected.items() if on]
    pool = [g for g in glossary if g["カテゴリ"] in enabled]
    if st.button("クイズを始める", type="primary"):
        if not enabled:
            st.error("カテゴリを1つ以上選んでください")
        elif len(pool) < total:
            st.error(f"選択中のカテゴリの用語数（{len(pool)}件）が設問数より少ないです")
        else:
            st.session_state["total"] = total
            st.session_state["pool"] = pool
            start_quiz()
            st.rerun()
    st.stop()

if st.session_state["finished"]:
    total = st.session_state.get("total", 10)
    st.subheader(f"🎉 クイズ終了！")
    st.metric("スコア", f"{st.session_state['score']} / {total}")
    score = st.session_state['score']
    ratio = score / total
    if score == 0:
        st.error("幼稚園からやり直してこい")
    elif ratio <= 0.3:
        st.warning("少々お勉強が必要ですわね、、、")
    elif ratio <= 0.7:
        st.info("なかなかですわ！基本はばっちりですわね！")
    elif ratio <= 0.9:
        st.success("流石でございますわ！！")
    else:
        st.success("カワバンガ！！")
    if st.button("もう一度", type="primary"):
        del st.session_state["questions"]
        st.rerun()

    st.divider()
    st.markdown("**📊 カテゴリ別結果**")
    from collections import defaultdict
    questions = st.session_state["questions"]
    wrong_terms = {w["term"] for w in st.session_state["wrong_answers"]}
    cat_total = defaultdict(int)
    cat_correct = defaultdict(int)
    for q in questions:
        cat_total[q["category"]] += 1
        if q["term"] not in wrong_terms:
            cat_correct[q["category"]] += 1
    for cat in sorted(cat_total):
        c, t = cat_correct[cat], cat_total[cat]
        st.write(f"{cat}：{c} / {t}")
    chart_data = pd.DataFrame(
        {"正解": [cat_correct[c] for c in sorted(cat_total)],
         "不正解": [cat_total[c] - cat_correct[c] for c in sorted(cat_total)]},
        index=sorted(cat_total),
    )
    st.bar_chart(chart_data, color=["#4CAF50", "#F44336"])

    wrongs = st.session_state["wrong_answers"]
    if wrongs:
        st.divider()
        st.markdown("**❌ 間違えた問題**")
        for w in wrongs:
            with st.expander(f"[{w['category']}] {w['term']}"):
                st.markdown(f"**あなたの回答：** {w['your_answer']}")
                st.markdown(f"**正解：** {w['correct_answer']}")
else:
    total = st.session_state.get("total", 10)
    idx = st.session_state["current"]
    q = st.session_state["questions"][idx]

    st.progress(idx / total, text=f"{idx + 1} / {total} 問目")
    st.markdown(f"**カテゴリ：{q['category']}**")
    st.subheader(f"「{q['term']}」の解説はどれ？")
    st.divider()

    for i, choice in enumerate(q["choices"]):
        if st.button(choice, key=f"choice_{i}", use_container_width=True, disabled=st.session_state["q_result"] is not None):
            if st.session_state["q_result"] is None:
                st.session_state["q_result"] = (choice == q["answer"])
                if st.session_state["q_result"]:
                    st.session_state["score"] += 1
                else:
                    st.session_state["wrong_answers"].append({
                        "category": q["category"],
                        "term": q["term"],
                        "your_answer": choice,
                        "correct_answer": q["answer"],
                    })

    if st.session_state["q_result"] is True:
        st.success("✅ 正解！")
    elif st.session_state["q_result"] is False:
        st.error(f"❌ 不正解… 正解は：\n\n{q['answer']}")

    if st.session_state["q_result"] is not None:
        is_last = (idx + 1 == total)
        label = "結果を見る 🏁" if is_last else "次の問題 ▶"
        if st.button(label, type="primary"):
            st.session_state["current"] += 1
            st.session_state["q_result"] = None
            if is_last:
                st.session_state["finished"] = True
            st.rerun()

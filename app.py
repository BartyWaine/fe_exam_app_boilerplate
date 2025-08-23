import streamlit as st
import pandas as pd
import os
import json
import ast
import random
import time

SAVE_FILE = "questions.json"
EXAM_DURATION = 6000  # 100 minutes

# ---------------------------
# Persistence Helpers
# ---------------------------
def load_saved_questions():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    return None

def save_questions(df):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2, ensure_ascii=False)

# ---------------------------
# Init session state
# ---------------------------
if "questions" not in st.session_state:
    st.session_state.questions = load_saved_questions()
if "exam_started" not in st.session_state:
    st.session_state.exam_started = False
if "exam_questions" not in st.session_state:
    st.session_state.exam_questions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None

st.title("📘 ITPEC FE Evening Exam Practice")

# ---------------------------
# Upload Questions
# ---------------------------
uploaded_file = st.file_uploader(
    "📂 Upload Questions File (CSV, JSON, Excel)", type=["csv", "json", "xlsx"]
)

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith(".json"):
        data = json.load(uploaded_file)
        if isinstance(data, dict) and "questions" in data:
            df = pd.DataFrame(data["questions"])
        else:
            df = pd.DataFrame(data)
    else:
        st.error("❌ Unsupported file format!")
        df = None

    if df is not None:
        save_questions(df)
        st.session_state.questions = df
        st.success(f"✅ Uploaded & saved {len(df)} questions!")

# ---------------------------
# Load Questions if Available
# ---------------------------
questions_df = st.session_state.questions

if questions_df is not None:
    st.info(f"📚 Loaded {len(questions_df)} questions from storage")

    if not st.session_state.exam_started:
        if st.button("🎯 Start Mock Exam (20 Random Questions)"):
            st.session_state.exam_questions = questions_df.sample(
                n=min(20, len(questions_df)), random_state=random.randint(0, 9999)
            )
            st.session_state.exam_started = True
            st.session_state.start_time = time.time()
            st.rerun()

# ---------------------------
# Exam Mode
# ---------------------------
if st.session_state.exam_started:
    st.subheader("📝 Exam In Progress")

    # Timer (100 minutes)
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, EXAM_DURATION - int(elapsed))
    mins, secs = divmod(remaining, 60)
    st.info(f"⏱️ Time Remaining: {mins}:{secs:02d}")

    for i, row in st.session_state.exam_questions.iterrows():
        st.write(f"**{row['id']}**: {row['question_text']}")

        raw_options = row["options"]
        if isinstance(raw_options, str):
            try:
                options = json.loads(raw_options)
            except:
                options = ast.literal_eval(raw_options)
        else:
            options = raw_options

        # Shuffle options each time
        options = random.sample(options, len(options))

        prev_answer = st.session_state.user_answers.get(row["id"])
        if prev_answer and prev_answer in options:
            default_index = options.index(prev_answer)
        else:
            default_index = 0

        st.session_state.user_answers[row["id"]] = st.radio(
            f"Select answer for {row['id']}",
            options,
            index=default_index,
            key=f"q_{row['id']}",
        )

    if st.button("✅ Submit Exam"):
        score = 0
        for _, q in st.session_state.exam_questions.iterrows():
            if st.session_state.user_answers.get(q["id"]) == q["correct_answer"]:
                score += 1

        st.success(f"🎉 Your Score: {score}/{len(st.session_state.exam_questions)}")

        # Review mode
        st.subheader("📖 Review")
        for _, q in st.session_state.exam_questions.iterrows():
            st.write(f"**{q['id']}**: {q['question_text']}")
            user_ans = st.session_state.user_answers.get(q["id"], "Not Answered")
            st.write(f"- Your Answer: {user_ans}")
            st.write(f"- Correct Answer: {q['correct_answer']}")
            st.caption(f"Explanation: {q.get('explanation', 'No explanation')}")

        # Reset for next run
        st.session_state.exam_started = False
        st.session_state.exam_questions = []
        st.session_state.user_answers = {}
        st.session_state.start_time = None

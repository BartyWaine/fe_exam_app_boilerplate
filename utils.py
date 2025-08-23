import json
import random
import pandas as pd
from fpdf import FPDF

def load_questions(file="questions.json"):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_exam(questions, n=20):
    return random.sample(questions, min(n, len(questions)))

def grade_exam(questions, user_answers):
    score = 0
    results = []
    for q in questions:
        correct = q["correct_answer"]
        user_ans = user_answers.get(q["id"], None)
        is_correct = (user_ans == correct)
        if is_correct:
            score += 1
        results.append({
            "id": q["id"],
            "question": q["question_text"],
            "user_answer": user_ans,
            "correct_answer": correct,
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })
    return score, results

def export_to_csv(results, file="exam_results.csv"):
    df = pd.DataFrame(results)
    df.to_csv(file, index=False)
    return file

def export_to_pdf(results, file="exam_results.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for r in results:
        pdf.multi_cell(0, 10, f"Q: {r['question']}")
        pdf.multi_cell(0, 10, f"Your Answer: {r['user_answer']}")
        pdf.multi_cell(0, 10, f"Correct Answer: {r['correct_answer']}")
        pdf.multi_cell(0, 10, f"Explanation: {r['explanation']}")
        pdf.ln(5)
    pdf.output(file)
    return file

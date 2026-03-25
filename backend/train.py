import os
import pickle
import re
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------- TEXT PREPROCESSING ----------
def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\b(pls|plz|u|ur)\b", "please", text)
    return re.sub(r"\s+", " ", text).strip()


# ---------- RETRAIN MODEL ----------
def retrain_model():
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )

    cursor = db.cursor()
    cursor.execute("SELECT question_clean, answer FROM faq")
    data = cursor.fetchall()
    db.close()

    if not data:
        print("❌ No data to train on")
        return

    questions = [q for q, _ in data if q]
    answers = [a for q, a in data if q]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(questions)

    os.makedirs("models", exist_ok=True)

    pickle.dump(vectorizer, open("models/vectorizer.pkl", "wb"))
    pickle.dump(matrix, open("models/matrix.pkl", "wb"))
    pickle.dump(answers, open("models/answers.pkl", "wb"))
    print("✅ Model retrained successfully")
if __name__ == "__main__":
    print("🔁 Manual training started...")
    retrain_model()
    print("✅ Manual training completed.")
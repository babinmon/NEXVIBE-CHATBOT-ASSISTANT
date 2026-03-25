from fastapi import FastAPI, Header, HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from nlp import get_response
from database import get_db
from security import verify_password
from auth import create_token, verify_token
import subprocess
from train import preprocess, retrain_model
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
app = FastAPI()
from db_init import init_db
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- MODELS ----------
class Message(BaseModel):
    message: str
    session_id: str


class AdminLogin(BaseModel):
    username: str
    password: str

class AdminAnswer(BaseModel):
    id: int
    question: str
    answer: str


# ---------- CHAT ----------
@app.post("/chat")
def chat(msg: Message):
    reply = get_response(msg.message, msg.session_id)
    return {"reply": reply}

# ---------- ADMIN LOGIN ----------
@app.post("/admin/login")
def admin_login(data: AdminLogin):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM admin WHERE username=%s",
        (data.username,)
    )
    admin = cursor.fetchone()
    db.close()

    if not admin:
        return {"success": False}

    if verify_password(data.password, admin["password"]):
        token = create_token(admin["username"], admin["role"])
        return {
            "success": True,
            "access_token": token,
            "role": admin["role"]
        }

    return {"success": False}


# ---------- VERIFY TOKEN DEPENDENCY ----------
def require_token(token: str = Header(...)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

# ---------- VIEW UNANSWERED (PROTECTED) ----------
@app.get("/admin/unanswered")
def get_unanswered(payload: dict = Depends(require_token)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM unanswered_questions")
    rows = cursor.fetchall()
    db.close()
    return rows


# ---------- SAVE ANSWER + RETRAIN (ADMIN ONLY) ----------
@app.post("/admin/answer")
def answer_question(
    data: AdminAnswer,
    payload: dict = Depends(require_token)
):
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    db = get_db()
    cursor = db.cursor()

    clean_q = preprocess(data.question)

    cursor.execute(
        "SELECT id FROM faq WHERE question_clean=%s",
        (clean_q,)
    )
    if cursor.fetchone():
    # 👇 remove from unanswered since it's already known
        cursor.execute(
            "DELETE FROM unanswered_questions WHERE id=%s",
            (data.id,)
        )
        db.commit()
        db.close()
        return {"status": "duplicate"}


    cursor.execute(
        "INSERT INTO faq (question, answer, question_clean) VALUES (%s, %s, %s)",
        (data.question, data.answer, clean_q)
    )

    cursor.execute(
        "DELETE FROM unanswered_questions WHERE id=%s",
        (data.id,)
    )

    db.commit()
    db.close()

    retrain_model()  # ✅ auto training

    return {"status": "answered"}
# ---------- DELETE UNANSWERED (ADMIN ONLY) ----------
@app.delete("/admin/unanswered/{qid}")
def delete_question(qid: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM unanswered_questions WHERE id=%s",
        (qid,)
    )
    db.commit()
    db.close()
    return {"status": "deleted"}

@app.post("/admin/cleanup")
def cleanup_duplicates(payload: dict = Depends(require_token)):
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch FAQ questions
    cursor.execute("SELECT question_clean FROM faq")
    faq_rows = cursor.fetchall()
    faq_questions = [r["question_clean"] for r in faq_rows if r["question_clean"]]

    if not faq_questions:
        db.close()
        return {"deleted": 0}

    # Fetch unanswered
    cursor.execute("SELECT id, question FROM unanswered_questions")
    unanswered = cursor.fetchall()

    if not unanswered:
        db.close()
        return {"deleted": 0}

    deleted_count = 0

    # ---------- CASE 1: MODEL NOT READY ----------
    if not os.path.exists("models/vectorizer.pkl"):
        for row in unanswered:
            clean_q = preprocess(row["question"])
            if clean_q in faq_questions:
                cursor.execute(
                    "DELETE FROM unanswered_questions WHERE id=%s",
                    (row["id"],)
                )
                deleted_count += 1

        db.commit()
        db.close()
        return {
            "deleted": deleted_count,
            "mode": "exact_only"
        }

    # ---------- CASE 2: MODEL EXISTS ----------
    vect = pickle.load(open("models/vectorizer.pkl", "rb"))
    faq_matrix = vect.transform(faq_questions)

    for row in unanswered:
        clean_q = preprocess(row["question"])
        user_vec = vect.transform([clean_q])
        similarity = cosine_similarity(user_vec, faq_matrix)
        best_score = similarity.max()

        if best_score >= 0.85:
            cursor.execute(
                "DELETE FROM unanswered_questions WHERE id=%s",
                (row["id"],)
            )
            deleted_count += 1

    db.commit()
    db.close()

    return {
        "deleted": deleted_count,
        "mode": "similarity"
    }

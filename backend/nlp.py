import re
import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity
from conversation_flows import FLOWS
from ai_fallback import ai_generate_response
from database import get_db
from ai_fallback import ai_generate_response
from train import preprocess   # ✅ single source of truth

CONFIDENCE_THRESHOLD = 0.20
FORCE_ADMIN_KEYWORDS = ["price", "cost", "custom", "legal", "refund"]

VECT_PATH = "models/vectorizer.pkl"
MATRIX_PATH = "models/matrix.pkl"
ANS_PATH = "models/answers.pkl"
SESSION_CONTEXT = {}
CHAT_HISTORY = {}

def handle_flow(session_id, user_input):
    context = SESSION_CONTEXT.get(session_id)
    if not context:
        return None

    flow = context["flow"]
    step = context["step"]
    flow_data = FLOWS.get(flow)
    current = flow_data.get(step)

    if "slot" in current:
        context["data"][current["slot"]] = user_input
        context["step"] += 1

    next_step = flow_data.get(context["step"])

    if "final" in next_step:
        SESSION_CONTEXT.pop(session_id)
        return next_step["final"]

    return next_step["question"]


# ---------- MODEL LOADER ----------
def load_model():
    if not (
        os.path.exists(VECT_PATH)
        and os.path.exists(MATRIX_PATH)
        and os.path.exists(ANS_PATH)
    ):
        return None, None, None

    vectorizer = pickle.load(open(VECT_PATH, "rb"))
    matrix = pickle.load(open(MATRIX_PATH, "rb"))
    answers = pickle.load(open(ANS_PATH, "rb"))
    return vectorizer, matrix, answers


# ---------- SAVE UNANSWERED (DUPLICATE SAFE) ----------
def save_unanswered(question):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id FROM unanswered_questions WHERE question=%s",
        (question,)
    )

    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO unanswered_questions (question) VALUES (%s)",
            (question,)
        )
        db.commit()

    db.close()


# ---------- MAIN CHAT LOGIC ----------
def get_response(user_input, session_id="default"):
    clean_input = preprocess(user_input)

    # init memory
    history = CHAT_HISTORY.get(session_id, [])

    # 1️⃣ CONTINUE ACTIVE FLOW
    flow_reply = handle_flow(session_id, clean_input)
    if flow_reply:
        history.append({"role": "assistant", "content": flow_reply})
        CHAT_HISTORY[session_id] = history
        return flow_reply

    # 2️⃣ START WEBSITE FLOW
    if "website" in clean_input:
        SESSION_CONTEXT[session_id] = {
            "flow": "website",
            "step": 1,
            "data": {}
        }
        reply = "Yes, we develop websites. " + FLOWS["website"][1]["question"]
        history.append({"role": "assistant", "content": reply})
        CHAT_HISTORY[session_id] = history
        return reply

    # 3️⃣ FAQ MATCH
    vectorizer, matrix, answers = load_model()
    if vectorizer and matrix is not None:
        user_vec = vectorizer.transform([clean_input])
        similarity = cosine_similarity(user_vec, matrix)
        best = similarity.argmax()
        confidence = similarity[0][best]

        if confidence >= CONFIDENCE_THRESHOLD:
            reply = answers[best]
            history.append({"role": "assistant", "content": reply})
            CHAT_HISTORY[session_id] = history
            return reply

    # 4️⃣ FULL LLaMA CONVERSATION (SAVE FOR ADMIN REVIEW)
    save_unanswered(user_input)
    reply, updated_history = ai_generate_response(
        user_input,
        history=history
    )
    CHAT_HISTORY[session_id] = updated_history
    return reply

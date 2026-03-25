async function login() {
  try {
    const res = await fetch("http://127.0.0.1:8000/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: user.value,
        password: pass.value
      })
    });

    const data = await res.json();

    if (data.success) {
      // ✅ SAVE TOKEN & ROLE
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("role", data.role);

      alert("Login successful");
      loadQuestions();
    } else {
      alert("Login failed");
    }
  } catch (err) {
    console.error(err);
    alert("Server not reachable");
  }
}

async function loadQuestions() {
  const role = localStorage.getItem("role");
if (role !== "admin") {
  alert("Unauthorized access");
  return;
}

  try {
    const token = localStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/admin/unanswered", {
      headers: {
        "token": token   // 🔐 JWT HEADER
      }
    });

    if (res.status === 401) {
      alert("Session expired. Please login again.");
      return;
    }

    const data = await res.json();

    const list = document.getElementById("questions");
    list.innerHTML = "";

    data.forEach(q => {
      const li = document.createElement("li");
      li.innerHTML = `
  <strong>${q.question}</strong>
  <input id="a${q.id}" placeholder="Answer">

  <div style="display:flex; gap:10px;">
    <button onclick="saveAnswer(${q.id}, \`${q.question}\`)">
      Answer
    </button>

    <button onclick="deleteQuestion(${q.id})"
            style="background:#dc2626;">
      Delete
    </button>
  </div>
`;

      list.appendChild(li);
    });

  } catch (err) {
    console.error(err);
    alert("Failed to load questions");
  }
}

// ✅ SAVE ANSWER & RETRAIN MODEL

async function saveAnswer(id, question) {
  try {
    const token = localStorage.getItem("token");
    const answer = document.getElementById("a" + id).value.trim();

    if (!answer) {
      alert("Please enter an answer");
      return;
    }

    const res = await fetch("http://127.0.0.1:8000/admin/answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "token": token
      },
      body: JSON.stringify({ id, question, answer })
    });

    const data = await res.json();

    if (data.status === "answered") {
      alert("Answer saved & model retrained");
    }
    else if (data.status === "duplicate") {
      alert("Question already exists in FAQ. Removed from pending list.");
    }

    // ✅ ALWAYS reload after success cases
    await loadQuestions();

  } catch (err) {
    console.error(err);
    alert("Failed to save answer");
  }
}

async function deleteQuestion(id) {
  if (!confirm("Are you sure you want to delete this question?")) return;

  const token = localStorage.getItem("token");

  await fetch(`http://127.0.0.1:8000/admin/unanswered/${id}`, {
    method: "DELETE",
    headers: {
      "token": token
    }
  });

  loadQuestions(); // disappears immediately
}
// ✅ CLEANUP DUPLICATE/SIMILAR QUESTIONS
async function cleanupDuplicates() {
  if (!confirm("This will remove duplicate/similar questions. Continue?")) return;

  const token = localStorage.getItem("token");

  const res = await fetch("http://127.0.0.1:8000/admin/cleanup", {
    method: "POST",
    headers: {
      "token": token
    }
  });

  const data = await res.json();

  alert(`Removed ${data.deleted} duplicate/similar questions`);
  loadQuestions(); // refresh UI
}



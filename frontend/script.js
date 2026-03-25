const sessionId =
  localStorage.getItem("session_id") || crypto.randomUUID();

localStorage.setItem("session_id", sessionId);
function toggleChat() {
  const bot = document.getElementById("chatbot");
  bot.style.display = bot.style.display === "none" ? "block" : "none";
}
async function sendMessage() {
  const input = document.getElementById("user-input");
  input.focus();
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, "user");
  input.value = "";

  showTyping();

  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
  message: text,
  session_id: sessionId
})
  });

  const data = await res.json();

  removeTyping();
  addMessage(data.reply, "bot");
}

function addMessage(text, sender) {
  const box = document.getElementById("chat-box");
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  msg.innerText = text;
  box.appendChild(msg);
  box.scrollTop = box.scrollHeight;
}

function showTyping() {
  const box = document.getElementById("chat-box");
  const typing = document.createElement("div");
  typing.id = "typing";
  typing.className = "message bot";
  typing.innerText = "Typing...";
  box.appendChild(typing);
  box.scrollTop = box.scrollHeight;
}

function removeTyping() {
  const typing = document.getElementById("typing");
  if (typing) typing.remove();
}


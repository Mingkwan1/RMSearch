const API_URL = "http://localhost:8000/ask"; // Change to your deployed API if needed

async function sendQuery() {
  const queryInput = document.getElementById('query');
  const chatBox = document.getElementById('chat-box');
  const query = queryInput.value.trim();

  if (!query) return;

  // Show user's message
  const userMsg = document.createElement('div');
  userMsg.className = 'message user';
  userMsg.innerText = `You: ${query}`;
  chatBox.appendChild(userMsg);

  // Clear input
  queryInput.value = "";

  // Get AI answer
  try {
      const response = await fetch("/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query })
      });

      const data = await response.json();

      const botMsg = document.createElement('div');
      botMsg.className = 'message bot';
      botMsg.innerText = `AI: ${data.answer}`;
      chatBox.appendChild(botMsg);

      // Auto-scroll to bottom
      chatBox.scrollTop = chatBox.scrollHeight;
  } catch (err) {
      const errMsg = document.createElement('div');
      errMsg.className = 'message bot';
      errMsg.innerText = "Error: Something went wrong.";
      chatBox.appendChild(errMsg);
  }
}

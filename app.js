const BACKEND_URL = "https://ga4-mcp-chat-257165300626.europe-west2.run.app/query"

// Check if user is already authenticated
document.addEventListener('DOMContentLoaded', () => {
  const savedPassword = sessionStorage.getItem("chat_password");
  if (savedPassword) {
    document.getElementById("password-screen").style.display = "none";
    document.getElementById("chat-screen").style.display = "block";
    document.getElementById("message").focus();
  }
  
  // Add cursor blinking effect to password input
  const passwordInput = document.getElementById("password");
  passwordInput.focus();
});

// Handle password authentication
document.getElementById("enter-btn").addEventListener("click", authenticateUser);
document.getElementById("password").addEventListener("keypress", e => {
  if (e.key === "Enter") authenticateUser();
});

function authenticateUser() {
  const password = document.getElementById("password").value;
  const errorElement = document.getElementById("password-error");
  
  if (!password) {
    errorElement.textContent = "Please enter a password";
    return;
  }
  
  // Simulate checking password (in a real app, this would be verified by the backend)
  errorElement.textContent = "";
  sessionStorage.setItem("chat_password", password);
  
  // Transition effect
  document.getElementById("password-screen").style.opacity = 0;
  setTimeout(() => {
    document.getElementById("password-screen").style.display = "none";
    document.getElementById("chat-screen").style.display = "block";
    setTimeout(() => {
      document.getElementById("chat-screen").style.opacity = 1;
      document.getElementById("message").focus();
    }, 50);
  }, 300);
}

document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("message").addEventListener("keypress", e => {
  if (e.key === "Enter") sendMessage();
});

// Add message to chat window with typewriter effect for bot messages
function appendMessage(role, text) {
  const div = document.createElement("div");
  div.classList.add("message", role);

  const label = document.createElement("span");
  label.classList.add("prompt");
  label.textContent = role === "user" ? "You > " : "GA4 > ";

  const content = document.createElement("span");
  
  div.appendChild(label);
  div.appendChild(content);
  document.getElementById("chat-window").appendChild(div);
  
  if (role === "bot") {
    // Typewriter effect for bot messages
    let i = 0;
    const speed = 10; // typing speed in milliseconds
    
    function typeWriter() {
      if (i < text.length) {
        content.textContent += text.charAt(i);
        i++;
        document.getElementById("chat-window").scrollTop = document.getElementById("chat-window").scrollHeight;
        setTimeout(typeWriter, speed);
      }
    }
    
    typeWriter();
  } else {
    // User messages appear instantly
    content.textContent = text;
    document.getElementById("chat-window").scrollTop = document.getElementById("chat-window").scrollHeight;
  }
}

// Send message to backend and handle response
async function sendMessage() {
  const messageInput = document.getElementById("message");
  const message = messageInput.value.trim();
  if (!message) return;
  
  // Disable input while processing
  messageInput.disabled = true;
  document.getElementById("send-btn").disabled = true;
  
  // Add user message to chat
  appendMessage("user", message);
  messageInput.value = "";
  
  // Show loading indicator
  const loadingDiv = document.createElement("div");
  loadingDiv.classList.add("message", "bot");
  const loadingLabel = document.createElement("span");
  loadingLabel.classList.add("prompt");
  loadingLabel.textContent = "GA4 > ";
  const loadingContent = document.createElement("span");
  loadingContent.classList.add("loading");
  loadingContent.textContent = "Processing query";
  loadingDiv.appendChild(loadingLabel);
  loadingDiv.appendChild(loadingContent);
  document.getElementById("chat-window").appendChild(loadingDiv);
  document.getElementById("chat-window").scrollTop = document.getElementById("chat-window").scrollHeight;
  
  try {
    const res = await fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        password: sessionStorage.getItem("chat_password"),
        message
      })
    });

    // Remove loading message
    document.getElementById("chat-window").removeChild(loadingDiv);
    
    if (!res.ok) {
      if (res.status === 401) {
        // Password invalid or expired
        appendMessage("bot", "Authentication failed. Please refresh and login again.");
        sessionStorage.removeItem("chat_password");
        setTimeout(() => {
          window.location.reload();
        }, 3000);
        return;
      }
      throw new Error(`Request failed with status ${res.status}`);
    }

    const data = await res.json();
    appendMessage("bot", data.reply);
  } catch (err) {
    appendMessage("bot", `Error: ${err.message}. Please try again later or check if the backend server is running.`);
  } finally {
    // Re-enable input
    messageInput.disabled = false;
    document.getElementById("send-btn").disabled = false;
    messageInput.focus();
  }
}

// Add command history functionality
let commandHistory = [];
let historyIndex = -1;

document.getElementById("message").addEventListener("keydown", e => {
  const messageInput = document.getElementById("message");
  
  if (e.key === "ArrowUp") {
    // Navigate up through command history
    if (historyIndex < commandHistory.length - 1) {
      historyIndex++;
      messageInput.value = commandHistory[historyIndex];
      // Move cursor to end of input
      setTimeout(() => {
        messageInput.selectionStart = messageInput.selectionEnd = messageInput.value.length;
      }, 0);
    }
    e.preventDefault();
  } else if (e.key === "ArrowDown") {
    // Navigate down through command history
    if (historyIndex > 0) {
      historyIndex--;
      messageInput.value = commandHistory[historyIndex];
    } else if (historyIndex === 0) {
      historyIndex = -1;
      messageInput.value = "";
    }
    e.preventDefault();
  } else if (e.key === "Enter") {
    const message = messageInput.value.trim();
    if (message) {
      // Add to command history (avoid duplicates)
      if (commandHistory.length === 0 || commandHistory[0] !== message) {
        commandHistory.unshift(message);
        // Limit history size
        if (commandHistory.length > 50) commandHistory.pop();
      }
      historyIndex = -1;
      sendMessage();
    }
  }
});

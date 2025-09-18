// ===============================
// Lamp Animation
// ===============================
let observer;

function initializeObserver() {
  const observerOptions = { threshold: 0.1, rootMargin: "0px 0px -50px 0px" };
  
  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animateLamp(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  // Observe all lamp containers
  document.querySelectorAll('.lamp-container').forEach(container => {
    observer.observe(container);
    container.style.opacity = '1';
  });
}

function animateLamp(container) {
  if (!container) return;

  const beamLeft = container.querySelector(".lamp-beam-left");
  const beamRight = container.querySelector(".lamp-beam-right");
  const glowMedium = container.querySelector(".lamp-glow-medium");
  const lightBeam = container.querySelector(".lamp-light-beam");
  const title = container.querySelector(".lamp-title");

  setTimeout(() => {
    [beamLeft, beamRight, glowMedium, lightBeam].forEach((el) =>
      el?.classList.add("animate")
    );
  }, 300);

  setTimeout(() => {
    title?.classList.add("animate");
  }, 600);
}

// ===============================
// Chat UI Class
// ===============================
class ChatUI {
  constructor() {
    this.chatMessages = document.getElementById("chatMessages");
    this.userInput = document.getElementById("userInput");
    this.sendButton = document.getElementById("sendButton");
    this.chatButton = document.getElementById("chatButton");
    this.chatSection = document.getElementById("chatSection");

    // Check if required elements exist
    if (!this.chatMessages || !this.userInput || !this.sendButton) {
      console.warn("⚠️ Some Chat UI elements are missing. Chat not fully initialized.");
      return;
    }

    // Initialize only if we have the minimum required elements
    if (this.chatSection) {
      this.chatSection.style.display = "none";
    }

    this.initializeEventListeners();
  }

  initializeEventListeners() {
    if (this.sendButton) {
      this.sendButton.addEventListener("click", () => this.handleSendMessage());
    }

    if (this.userInput) {
      this.userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.handleSendMessage();
        }
      });
    }

    if (this.chatButton && this.chatSection) {
      this.chatButton.addEventListener("click", (e) => {
        e.preventDefault();
        this.chatSection.style.display = "block";
        this.chatSection.scrollIntoView({ behavior: "smooth" });
        this.userInput?.focus();
      });
    }
  }

  async handleSendMessage() {
    const message = this.userInput.value.trim();
    if (!message) return;

    this.addMessage("user", message);
    this.userInput.value = "";

    const typingId = this.showTypingIndicator();

    try {
      const response = await this.sendToBackend(message);

      this.removeTypingIndicator(typingId);
      this.addMessage(
        "bot",
        response?.final_answer || "I couldn't process your request. Please try again."
      );
    } catch (error) {
      console.error("Error:", error);
      this.removeTypingIndicator(typingId);
      this.addMessage(
        "bot",
        "Sorry, I encountered an error. Please try again later."
      );
    }
  }

  async sendToBackend(message) {
    const response = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  }

  addMessage(sender, text) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
  }

  showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "typing-indicator";
    typingDiv.id = "typing-indicator";

    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("div");
      dot.className = "typing-dot";
      typingDiv.appendChild(dot);
    }

    this.chatMessages.appendChild(typingDiv);
    this.scrollToBottom();
    return typingDiv.id;
  }

  removeTypingIndicator(id) {
    document.getElementById(id)?.remove();
  }

  scrollToBottom() {
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }
}

// ===============================
// Initialize Application
// ===============================
function initializeApp() {
  // Initialize observer for lamp animations
  initializeObserver();
  
  // Initialize chat UI if the chat section exists
  if (document.getElementById('chatSection')) {
    window.chatUI = new ChatUI();
  }
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', initializeApp);

// Export ChatUI for global access if using modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ChatUI };
}

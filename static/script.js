// ===============================
// Lamp Animation
// ===============================
let observer;

// Function to check if DOM is ready
function domReady(callback) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', callback);
  } else {
    callback();
  }
}

function initializeObserver() {
  try {
    const lampContainers = document.querySelectorAll('.lamp-container');
    if (!lampContainers.length) {
      console.warn('No lamp containers found');
      return;
    }

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
    lampContainers.forEach(container => {
      if (container) {
        observer.observe(container);
        container.style.opacity = '1';
      }
    });
  } catch (error) {
    console.error('Error initializing observer:', error);
  }
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
  static isInitialized = false;
  constructor() {
    if (ChatUI.isInitialized) {
      console.log('ChatUI already initialized');
      return;
    }

    try {
      this.chatMessages = document.getElementById("chatMessages");
      this.userInput = document.getElementById("userInput");
      this.sendButton = document.getElementById("sendButton");
      this.chatButton = document.getElementById("chatButton");
      this.chatSection = document.getElementById("chatSection");

      // Check if required elements exist
      if (!this.chatMessages || !this.userInput || !this.sendButton) {
        console.warn("⚠️ Some Chat UI elements are missing. Chat not fully initialized.", {
          chatMessages: !!this.chatMessages,
          userInput: !!this.userInput,
          sendButton: !!this.sendButton
        });
        return;
      }

      // Initialize only if we have the minimum required elements
      if (this.chatSection) {
        this.chatSection.style.display = "none";
      }

      this.initializeEventListeners();
      ChatUI.isInitialized = true;
      console.log('ChatUI initialized successfully');
    } catch (error) {
      console.error('Error initializing ChatUI:', error);
    }
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
  try {
    // Prevent multiple initializations
    if (window.appInitialized) {
      console.log('Application already initialized');
      return;
    }
    
    console.log('Initializing application...');
    
    // Initialize observer for lamp animations
    if (typeof initializeObserver === 'function') {
      initializeObserver();
    } else {
      console.warn('initializeObserver function not found');
    }
    
    // Initialize chat UI if the chat section exists
    if (document.getElementById('chatSection')) {
      window.chatUI = new ChatUI();
    } else {
      console.warn('Chat section not found in the DOM');
    }
    
    // Set the flag to indicate the app is initialized
    window.appInitialized = true;
    console.log('Application initialized successfully');
  } catch (error) {
    console.error('Error initializing application:', error);
  }
}

// Initialize the application when the DOM is ready
domReady(function() {
  // Small delay to ensure all elements are available
  setTimeout(initializeApp, 100);
});

// Export ChatUI for global access if using modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ChatUI, initializeApp };
}

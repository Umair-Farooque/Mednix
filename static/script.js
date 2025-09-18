// Intersection Observer for scroll-triggered animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const container = entry.target;
            animateLamp(container);
        }
    });
}, observerOptions);

// Function to animate lamp elements
function animateLamp(container) {
    const beamLeft = container.querySelector('.lamp-beam-left');
    const beamRight = container.querySelector('.lamp-beam-right');
    const glowMedium = container.querySelector('.lamp-glow-medium');
    const lightBeam = container.querySelector('.lamp-light-beam');
    const title = container.querySelector('.lamp-title');

    // Add animation classes with slight delays
    setTimeout(() => {
        if (beamLeft) beamLeft.classList.add('animate');
        if (beamRight) beamRight.classList.add('animate');
        if (glowMedium) glowMedium.classList.add('animate');
        if (lightBeam) lightBeam.classList.add('animate');
    }, 300);

    setTimeout(() => {
        if (title) title.classList.add('animate');
    }, 600);
}

// Chat functionality
class ChatUI {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatButton = document.getElementById('chatButton');
        this.chatSection = document.getElementById('chatSection');
        
        // Hide chat section by default
        this.chatSection.style.display = 'none';
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => this.handleSendMessage());
        
        // Send message on Enter key
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        // Scroll to chat section when chat button is clicked
        if (this.chatButton) {
            this.chatButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.chatSection.style.display = 'block';
                this.chatSection.scrollIntoView({ behavior: 'smooth' });
                this.userInput.focus();
            });
        }
    }

    async handleSendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);
        this.userInput.value = '';

        // Show typing indicator
        const typingId = this.showTypingIndicator();

        try {
            // Call your FastAPI endpoint here
            const response = await this.sendToBackend(message);
            
            // Remove typing indicator and add bot response
            this.removeTypingIndicator(typingId);
            this.addMessage('bot', response.answer || 'I apologize, but I encountered an error processing your request.');
        } catch (error) {
            console.error('Error:', error);
            this.removeTypingIndicator(typingId);
            this.addMessage('bot', 'Sorry, I encountered an error. Please try again later.');
        }
    }

    async sendToBackend(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error sending message to backend:', error);
            throw error;
        }
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        // Add three dots
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingDiv.appendChild(dot);
        }
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
        
        return 'typing-indicator';
    }

    removeTypingIndicator(id) {
        const typingElement = document.getElementById(id);
        if (typingElement) {
            typingElement.remove();
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize the chat UI when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize lamp animations
    const lampContainers = document.querySelectorAll('.lamp-container');
    lampContainers.forEach(container => {
        observer.observe(container);
    });

    // Initialize chat functionality
    if (document.getElementById('chatSection')) {
        new ChatUI();
    }
});

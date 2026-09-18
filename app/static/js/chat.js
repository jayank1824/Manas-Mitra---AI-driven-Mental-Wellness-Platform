// Chat functionality for AI Consultant
class ConsultantChat {
    constructor() {
        this.chatContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.clearButton = document.getElementById('clear-chat-btn');
        this.quickSuggestions = document.getElementById('quick-suggestions');
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
        
        this.clearButton.addEventListener('click', () => {
            if (confirm("Are you sure you want to clear the conversation history?")) {
                this.clearChat();
            }
        });

        // Setup suggestion chips
        document.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                this.messageInput.value = chip.textContent;
                this.sendMessage();
            });
        });
        
        this.loadHistory();
    }
    
    async loadHistory() {
        try {
            const response = await fetch('/consultant/history');
            const data = await response.json();
            
            this.chatContainer.innerHTML = '';
            
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    this.addMessage(msg.content, msg.role, msg.created_at);
                });
                this.quickSuggestions.classList.remove('hidden');
            } else {
                // Initial welcome message
                const welcomeMsg = "Hello! 👋 I'm Dr. Manas, your AI mental wellness companion. How are you feeling today?";
                this.addMessage(welcomeMsg, 'assistant', new Date().toISOString());
                this.quickSuggestions.classList.remove('hidden');
            }
            
            this.scrollToBottom();
        } catch (error) {
            console.error("Error loading chat history:", error);
            this.chatContainer.innerHTML = '<div class="text-center text-red-500 py-4">Failed to load chat history.</div>';
        }
    }
    
    async sendMessage() {
        if (this.isLoading) return;
        
        const content = this.messageInput.value.trim();
        if (!content) return;
        
        // Reset input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.quickSuggestions.classList.add('hidden');
        
        // Show user message
        this.addMessage(content, 'user', new Date().toISOString());
        this.scrollToBottom();
        
        // Show loading
        this.isLoading = true;
        this.showLoading();
        this.scrollToBottom();
        
        try {
            const response = await fetch('/consultant/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: content })
            });
            
            const data = await response.json();
            
            this.hideLoading();
            
            if (response.ok) {
                this.addMessage(data.response, 'assistant', data.timestamp);
            } else {
                this.addMessage("Sorry, I encountered an error. Please try again.", 'assistant', new Date().toISOString());
            }
        } catch (error) {
            console.error("Error sending message:", error);
            this.hideLoading();
            this.addMessage("Network error. Please check your connection and try again.", 'assistant', new Date().toISOString());
        } finally {
            this.isLoading = false;
            this.scrollToBottom();
        }
    }
    
    formatTime(isoString) {
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    formatContent(content) {
        // Basic markdown formatting
        let formatted = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        return formatted;
    }
    
    addMessage(content, role, timestamp) {
        const div = document.createElement('div');
        div.className = `flex w-full ${role === 'user' ? 'justify-end' : 'justify-start'}`;
        
        const timeStr = this.formatTime(timestamp);
        const formattedContent = this.formatContent(content);
        
        if (role === 'user') {
            div.innerHTML = `
                <div class="flex flex-col items-end max-w-[85%] sm:max-w-[75%]">
                    <div class="bg-teal-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-sm text-sm sm:text-base">
                        ${formattedContent}
                    </div>
                    <span class="text-xs text-gray-400 mt-1">${timeStr}</span>
                </div>
            `;
        } else {
            div.innerHTML = `
                <div class="flex items-end space-x-2 max-w-[85%] sm:max-w-[75%]">
                    <div class="flex-shrink-0 mb-5">
                        <div class="h-8 w-8 rounded-full bg-teal-100 flex items-center justify-center text-teal-600 text-xl shadow-sm border border-teal-200">
                            🤖
                        </div>
                    </div>
                    <div class="flex flex-col items-start">
                        <div class="bg-white text-gray-800 rounded-2xl rounded-bl-sm px-4 py-3 shadow-md border border-gray-100 text-sm sm:text-base">
                            ${formattedContent}
                        </div>
                        <span class="text-xs text-gray-400 mt-1 ml-1">${timeStr}</span>
                    </div>
                </div>
            `;
        }
        
        this.chatContainer.appendChild(div);
    }
    
    showLoading() {
        const div = document.createElement('div');
        div.id = 'typing-indicator';
        div.className = 'flex w-full justify-start';
        div.innerHTML = `
            <div class="flex items-end space-x-2">
                <div class="flex-shrink-0 mb-1">
                    <div class="h-8 w-8 rounded-full bg-teal-100 flex items-center justify-center text-teal-600 text-xl">
                        🤖
                    </div>
                </div>
                <div class="bg-white text-gray-500 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm border border-gray-100">
                    <div class="typing-indicator flex items-center h-4">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        this.chatContainer.appendChild(div);
    }
    
    hideLoading() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }, 50);
    }
    
    async clearChat() {
        try {
            const response = await fetch('/consultant/clear', {
                method: 'POST'
            });
            if (response.ok) {
                this.chatContainer.innerHTML = '';
                const welcomeMsg = "Chat history cleared. How can I help you today? 🌱";
                this.addMessage(welcomeMsg, 'assistant', new Date().toISOString());
                this.quickSuggestions.classList.remove('hidden');
            }
        } catch (error) {
            console.error("Error clearing chat:", error);
        }
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    new ConsultantChat();
});

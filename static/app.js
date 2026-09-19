const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');
const loadingIndicator = document.getElementById('loading-indicator');

// Global conversation state
let messages = [];

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message to UI
    addMessageToUI('user', text);
    messages.push({ role: 'user', content: text });
    
    userInput.value = '';
    userInput.disabled = true;
    loadingIndicator.style.display = 'flex';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ messages })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        messages.push({ role: 'assistant', content: data.response });
        
        // Parse markdown and render
        addMessageToUI('assistant', marked.parse(data.response));
        
    } catch (error) {
        console.error('Error:', error);
        addMessageToUI('assistant', 'Sorry, I encountered an error connecting to the server.');
    } finally {
        userInput.disabled = false;
        loadingIndicator.style.display = 'none';
        userInput.focus();
    }
});

function addMessageToUI(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (role === 'user') {
        contentDiv.textContent = content; // raw text for user
    } else {
        contentDiv.innerHTML = content; // parsed html for bot
    }
    
    div.appendChild(contentDiv);
    chatBox.appendChild(div);
    
    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ===== Global State =====
let sessionId = 'session_' + Date.now();
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// ===== DOM Elements =====
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const micButton = document.getElementById('micButton');
const sendButton = document.getElementById('sendButton');

// ===== Event Listeners =====
sendButton.addEventListener('click', handleSendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSendMessage();
    }
});
micButton.addEventListener('click', toggleRecording);

// ===== Functions =====

async function handleSendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // 1. Add User Message
    addMessage(text, 'user');
    messageInput.value = '';

    // 2. Show Typing Indicator
    const typingId = showTypingIndicator();

    try {
        // 3. Send to Backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                session_id: sessionId
            })
        });

        if (!response.ok) throw new Error('API Error');
        const data = await response.json();

        // 4. Remove Typing Indicator & Add Bot Message
        removeTypingIndicator(typingId);
        addMessage(data.response, 'bot');

    } catch (error) {
        console.error(error);
        removeTypingIndicator(typingId);
        addMessage('Sorry, something went wrong. | عذراً، حدث خطأ.', 'bot');
    }
}

async function toggleRecording() {
    if (!isRecording) {
        // Start Recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                // Send Audio when recording stops
                await sendVoiceMessage();
            };

            mediaRecorder.start();
            isRecording = true;
            micButton.classList.add('listening');

        } catch (err) {
            console.error('Mic Error:', err);
            alert('Cannot access microphone.');
        }
    } else {
        // Stop Recording
        if (mediaRecorder) {
            mediaRecorder.stop();
            // Stop all tracks to release mic
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
        isRecording = false;
        micButton.classList.remove('listening');
    }
}

async function sendVoiceMessage() {
    if (audioChunks.length === 0) return;

    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    formData.append('session_id', sessionId);

    // Show typing indicator while processing voice
    const typingId = showTypingIndicator();

    try {
        const response = await fetch('/api/voice-chat', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Voice API Error');
        const data = await response.json();

        removeTypingIndicator(typingId);

        if (data.error) {
            addMessage(data.error, 'bot');
        } else {
            // Show transcription if available
            if (data.transcription) {
                addMessage(`🎤 ${data.transcription}`, 'user');
            }
            addMessage(data.response, 'bot');
        }

    } catch (error) {
        console.error(error);
        removeTypingIndicator(typingId);
        addMessage('Error processing voice message.', 'bot');
    }
}

function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Render Markdown for bot, plain text for user
    if (sender === 'bot') {
        // Use marked.parse if available (since we added the script)
        bubble.innerHTML = window.marked ? marked.parse(content) : content;
    } else {
        bubble.textContent = content;
    }

    contentDiv.appendChild(bubble);

    if (sender === 'bot') {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
    } else {
        // User: Content first (flex-direction: row-reverse handles visual order, 
        // but DOM order is avatar then content, css reverses it)
        // Wait, CSS says: .message.user { flex-direction: row-reverse; }
        // So DOM order: Avatar, Content. Visual: Content, Avatar.
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = id;

    typingDiv.innerHTML = `
        <div class="message-avatar" style="background: #3b82f6; color: white;">🤖</div>
        <div class="typing-bubble">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;

    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Initial Greeting Timestamp
const initialTime = document.getElementById('initialTime');
if (initialTime) {
    const now = new Date();
    initialTime.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

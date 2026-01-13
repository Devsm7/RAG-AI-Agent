// ===== Global State =====
let currentTab = 'text';
let textSessionId = 'text_session_' + Date.now();
let voiceSessionId = 'voice_session_' + Date.now();
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// ===== DOM Elements =====
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

// Text Chat Elements
const textInput = document.getElementById('text-input');
const textSendBtn = document.getElementById('text-send-btn');
const textClearBtn = document.getElementById('text-clear-btn');
const textChatbox = document.getElementById('text-chatbox');

// Voice Chat Elements
const recordBtn = document.getElementById('record-btn');
const voiceSendBtn = document.getElementById('voice-send-btn');
const voiceClearBtn = document.getElementById('voice-clear-btn');
const voiceChatbox = document.getElementById('voice-chatbox');
const recordingStatus = document.getElementById('recording-status');

// Loading Overlay
const loadingOverlay = document.getElementById('loading-overlay');

// Example Cards
const exampleCards = document.querySelectorAll('.example-card');

// ===== Tab Switching =====
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    currentTab = tabName;

    // Update buttons
    tabButtons.forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Update content
    tabContents.forEach(content => {
        if (content.id === `${tabName}-tab`) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

// ===== Text Chat Functions =====
textSendBtn.addEventListener('click', sendTextMessage);
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendTextMessage();
    }
});

async function sendTextMessage() {
    const message = textInput.value.trim();

    if (!message) {
        return;
    }

    // Add user message to chat
    addMessage(textChatbox, message, 'user');

    // Clear input
    textInput.value = '';

    // Show loading
    showLoading();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: textSessionId
            })
        });

        if (!response.ok) {
            throw new Error('Failed to get response');
        }

        const data = await response.json();

        // Add bot response to chat
        addMessage(textChatbox, data.response, 'bot');

    } catch (error) {
        console.error('Error:', error);
        addMessage(textChatbox, 'Sorry, there was an error processing your request. | عذراً، حدث خطأ في معالجة طلبك.', 'bot', true);
    } finally {
        hideLoading();
    }
}

textClearBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear the conversation? | هل أنت متأكد من مسح المحادثة؟')) {
        try {
            await fetch('/api/clear-history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: textSessionId
                })
            });

            // Clear chatbox
            textChatbox.innerHTML = `
                <div class="welcome-message">
                    <div class="bot-avatar">🤖</div>
                    <div class="message-content">
                        <p><strong>Welcome! مرحباً!</strong></p>
                        <p>I'm here to help you with information about Twuaiq Academy bootcamps, locations, and schedules.</p>
                        <p>أنا هنا لمساعدتك بمعلومات حول معسكرات أكاديمية طويق والمواقع والجداول.</p>
                    </div>
                </div>
            `;

            // Generate new session ID
            textSessionId = 'text_session_' + Date.now();

        } catch (error) {
            console.error('Error clearing history:', error);
        }
    }
});

// ===== Voice Chat Functions =====
recordBtn.addEventListener('click', toggleRecording);
voiceSendBtn.addEventListener('click', sendVoiceMessage);
voiceClearBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear the conversation? | هل أنت متأكد من مسح المحادثة؟')) {
        try {
            await fetch('/api/clear-history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: voiceSessionId
                })
            });

            // Clear chatbox
            voiceChatbox.innerHTML = `
                <div class="welcome-message">
                    <div class="bot-avatar">🤖</div>
                    <div class="message-content">
                        <p><strong>Voice Chat Ready! الدردشة الصوتية جاهزة!</strong></p>
                        <p>Click the microphone button below to record your question.</p>
                        <p>انقر على زر الميكروفون أدناه لتسجيل سؤالك.</p>
                    </div>
                </div>
            `;

            // Generate new session ID
            voiceSessionId = 'voice_session_' + Date.now();

            // Reset recording state
            audioChunks = [];
            voiceSendBtn.disabled = true;

        } catch (error) {
            console.error('Error clearing history:', error);
        }
    }
});

async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            // Enable send button
            voiceSendBtn.disabled = false;
        };

        mediaRecorder.start();
        isRecording = true;

        // Update UI
        recordBtn.classList.add('recording');
        recordBtn.querySelector('.record-text').textContent = 'Stop Recording | إيقاف التسجيل';
        recordingStatus.classList.remove('hidden');

    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Could not access microphone. Please check your permissions. | لا يمكن الوصول إلى الميكروفون. يرجى التحقق من الأذونات.');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;

        // Update UI
        recordBtn.classList.remove('recording');
        recordBtn.querySelector('.record-text').textContent = 'Click to Record | انقر للتسجيل';
        recordingStatus.classList.add('hidden');
    }
}

async function sendVoiceMessage() {
    if (audioChunks.length === 0) {
        return;
    }

    showLoading();

    try {
        // Create audio blob
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('session_id', voiceSessionId);

        const response = await fetch('/api/voice-chat', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to process voice message');
        }

        const data = await response.json();

        if (data.error) {
            addMessage(voiceChatbox, data.error, 'bot', true);
        } else {
            // Add transcription as user message
            addMessage(voiceChatbox, `🎤 ${data.transcription}`, 'user');

            // Add bot response
            addMessage(voiceChatbox, data.response, 'bot');
        }

        // Reset
        audioChunks = [];
        voiceSendBtn.disabled = true;

    } catch (error) {
        console.error('Error:', error);
        addMessage(voiceChatbox, 'Sorry, there was an error processing your voice message. | عذراً، حدث خطأ في معالجة رسالتك الصوتية.', 'bot', true);
    } finally {
        hideLoading();
    }
}

// ===== Helper Functions =====
function addMessage(chatbox, content, sender, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = content;

    if (isError) {
        bubble.style.borderLeftColor = 'var(--error-color)';
        bubble.style.color = 'var(--error-color)';
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);

    chatbox.appendChild(messageDiv);

    // Scroll to bottom
    chatbox.scrollTop = chatbox.scrollHeight;
}

function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

// ===== Example Questions =====
exampleCards.forEach(card => {
    card.addEventListener('click', () => {
        const question = card.dataset.question;
        textInput.value = question;
        textInput.focus();

        // Switch to text tab if not already there
        if (currentTab !== 'text') {
            switchTab('text');
        }
    });
});

// ===== Initialize =====
console.log('🎓 Twuaiq Academy Assistant initialized');
console.log('Text Session ID:', textSessionId);
console.log('Voice Session ID:', voiceSessionId);

// Check if browser supports media recording
if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    console.warn('Voice recording not supported in this browser');
    recordBtn.disabled = true;
    recordBtn.querySelector('.record-text').textContent = 'Voice not supported | الصوت غير مدعوم';
}

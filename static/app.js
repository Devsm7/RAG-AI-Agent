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

            // Add bot response with audio if available
            addMessage(data.response, 'bot', data.audio_base64);

            // Try autoplay as well
            if (data.audio_base64) {
                console.log('🎵 Audio found, attempting autoplay...');
                playTTSAudio(data.audio_base64);
            }
        }

    } catch (error) {
        console.error(error);
        removeTypingIndicator(typingId);
        addMessage('Error processing voice message.', 'bot');
    }
}

function addMessage(content, sender, audioBase64 = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Render Markdown for bot, plain text for user
    if (sender === 'bot') {
        bubble.innerHTML = window.marked ? marked.parse(content) : content;

        // Add Play Button if audio is available
        if (audioBase64) {
            const playBtn = document.createElement('button');
            playBtn.innerHTML = '🔊 Play Audio';
            playBtn.className = 'play-audio-btn';
            playBtn.style.cssText = `
                display: block;
                margin-top: 8px;
                padding: 6px 12px;
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 12px;
                cursor: pointer;
                font-size: 12px;
                color: #374151;
                transition: all 0.2s;
                font-weight: 500;
            `;
            playBtn.onmouseover = () => {
                playBtn.style.background = '#e5e7eb';
                playBtn.style.transform = 'scale(1.02)';
            };
            playBtn.onmouseout = () => {
                playBtn.style.background = '#f3f4f6';
                playBtn.style.transform = 'scale(1)';
            };
            playBtn.onclick = () => playTTSAudio(audioBase64);

            bubble.appendChild(playBtn);
        }
    } else {
        bubble.textContent = content;
    }

    contentDiv.appendChild(bubble);

    if (sender === 'bot') {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
    } else {
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

function playTTSAudio(base64Audio) {
    console.log('🎵 playTTSAudio called');

    if (!base64Audio) {
        console.error('❌ No audio data provided');
        return;
    }

    try {
        // Decode base64 to binary
        const binaryString = atob(base64Audio);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        // Create blob and URL
        const audioBlob = new Blob([bytes], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);

        // Create or get audio element
        let audioPlayer = document.getElementById('tts-audio-player');
        if (!audioPlayer) {
            audioPlayer = document.createElement('audio');
            audioPlayer.id = 'tts-audio-player';
            audioPlayer.controls = false;
            document.body.appendChild(audioPlayer);
        }

        // Set source and play
        audioPlayer.src = audioUrl;
        console.log('▶️ Attempting to play audio...');

        audioPlayer.play().then(() => {
            console.log('✅ Audio playing successfully!');
            showSpeakingIndicator();
        }).catch(err => {
            console.error('❌ Error playing audio:', err);
            console.error('Error details:', err.name, err.message);
            // Don't alert, just log. The button is there for manual play.
        });

        // Clean up when done
        audioPlayer.onended = () => {
            console.log('🏁 Audio playback finished');
            URL.revokeObjectURL(audioUrl);
            hideSpeakingIndicator();
        };

        // Add error handler
        audioPlayer.onerror = (e) => {
            console.error('❌ Audio element error:', e);
            hideSpeakingIndicator();
        };

    } catch (error) {
        console.error('❌ Error in playTTSAudio:', error);
    }
}

function showSpeakingIndicator() {
    const header = document.querySelector('.chat-header');
    let speakerIcon = document.getElementById('speaker-indicator');

    if (!speakerIcon) {
        speakerIcon = document.createElement('div');
        speakerIcon.id = 'speaker-indicator';
        speakerIcon.style.cssText = `
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 24px;
            animation: pulse 1s infinite;
        `;
        speakerIcon.textContent = '🔊';
        header.style.position = 'relative';
        header.appendChild(speakerIcon);
    }
}

function hideSpeakingIndicator() {
    const speakerIcon = document.getElementById('speaker-indicator');
    if (speakerIcon) {
        speakerIcon.remove();
    }
}

// Initial Greeting Timestamp
const initialTime = document.getElementById('initialTime');
if (initialTime) {
    const now = new Date();
    initialTime.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

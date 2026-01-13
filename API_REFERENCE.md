# 📡 API Quick Reference

## Base URL
```
http://localhost:8000
```

## Endpoints Summary

| Endpoint | Method | Request Type | Response Type | Purpose |
|----------|--------|--------------|---------------|---------|
| `/` | GET | - | HTML | Web interface |
| `/api/chat` | POST | JSON | JSON | Text chat |
| `/api/voice-chat` | POST | multipart/form-data | JSON | Voice chat |
| `/api/clear-history` | POST | JSON | JSON | Clear session |
| `/api/health` | GET | - | JSON | Health check |
| `/docs` | GET | - | HTML | Swagger UI |
| `/redoc` | GET | - | HTML | ReDoc UI |

---

## 1. Text Chat

### POST `/api/chat`

**Request** (Content-Type: `application/json`):
```json
{
  "message": "What bootcamps are available?",
  "session_id": "optional_session_id"
}
```

**Response** (application/json):
```json
{
  "response": "The available bootcamps are...",
  "session_id": "session_id"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What bootcamps are available?",
    "session_id": "my_session"
  }'
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "What bootcamps are available?",
        "session_id": "my_session"
    }
)
data = response.json()
print(f"Response: {data['response']}")
```

**JavaScript Example**:
```javascript
fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: 'What bootcamps are available?',
        session_id: 'my_session'
    })
})
.then(r => r.json())
.then(data => console.log(data.response));
```

---

## 2. Voice Chat

### POST `/api/voice-chat`

**Request** (Content-Type: `multipart/form-data`):
- **Field 1**: `audio` (file) - WAV audio file
- **Field 2**: `session_id` (string, optional) - Default: "voice_session"

**Response** (application/json):
```json
{
  "transcription": "What bootcamps are available?",
  "response": "The available bootcamps are...",
  "session_id": "voice_session"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/voice-chat" \
  -F "audio=@recording.wav" \
  -F "session_id=my_voice_session"
```

**Python Example**:
```python
import requests

with open("recording.wav", "rb") as audio_file:
    response = requests.post(
        "http://localhost:8000/api/voice-chat",
        files={"audio": audio_file},
        data={"session_id": "my_session"}
    )

data = response.json()
print(f"Transcription: {data['transcription']}")
print(f"Response: {data['response']}")
```

**JavaScript Example** (with File Upload):
```javascript
const formData = new FormData();
formData.append('audio', audioBlob, 'recording.wav');
formData.append('session_id', 'my_session');

fetch('http://localhost:8000/api/voice-chat', {
    method: 'POST',
    body: formData
})
.then(r => r.json())
.then(data => {
    console.log('Transcription:', data.transcription);
    console.log('Response:', data.response);
});
```

---

## 3. Clear History

### POST `/api/clear-history`

**Request** (Content-Type: `application/json`):
```json
{
  "session_id": "my_session"
}
```

**Response** (application/json):
```json
{
  "message": "History cleared",
  "session_id": "my_session"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/clear-history" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my_session"}'
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/clear-history",
    json={"session_id": "my_session"}
)
print(response.json())
```

---

## 4. Health Check

### GET `/api/health`

**Request**: No body required

**Response** (application/json):
```json
{
  "status": "healthy",
  "model": "aya:8b",
  "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/health"
```

**Python Example**:
```python
import requests

response = requests.get("http://localhost:8000/api/health")
print(response.json())
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request**:
```json
{
  "detail": "Message cannot be empty"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Error generating response: <error message>"
}
```

---

## Request/Response Summary

### Text Chat (`/api/chat`)
- ✅ **Request**: JSON
- ✅ **Response**: JSON

### Voice Chat (`/api/voice-chat`)
- ❌ **Request**: multipart/form-data (NOT JSON - file upload)
- ✅ **Response**: JSON

### Clear History (`/api/clear-history`)
- ✅ **Request**: JSON
- ✅ **Response**: JSON

### Health Check (`/api/health`)
- ✅ **Request**: None
- ✅ **Response**: JSON

---

## Testing with Swagger UI

Visit http://localhost:8000/docs to:
- See interactive API documentation
- Test endpoints directly in browser
- View request/response schemas
- Try different parameters

---

## Common Use Cases

### 1. Simple Q&A Bot
```python
import requests

def ask_question(question):
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={"message": question}
    )
    return response.json()["response"]

answer = ask_question("What bootcamps are available?")
print(answer)
```

### 2. Voice Assistant
```python
import requests

def transcribe_and_answer(audio_file_path):
    with open(audio_file_path, "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/voice-chat",
            files={"audio": f}
        )
    data = response.json()
    return data["transcription"], data["response"]

transcript, answer = transcribe_and_answer("question.wav")
print(f"You said: {transcript}")
print(f"Answer: {answer}")
```

### 3. Conversation with History
```python
import requests

session_id = "user_123"

def chat(message):
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={
            "message": message,
            "session_id": session_id
        }
    )
    return response.json()["response"]

# Conversation
print(chat("What bootcamps are available?"))
print(chat("Tell me more about the first one"))  # Uses history
print(chat("What time does it start?"))  # Uses history
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_message: ChatMessage):
    # ...
```

---

## CORS Configuration

Currently allows all origins (`*`). For production, restrict to specific domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

**For full documentation, visit: http://localhost:8000/docs**

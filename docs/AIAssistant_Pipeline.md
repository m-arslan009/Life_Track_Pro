# AI Assistant API Pipeline Documentation

## Overview
This document describes the complete request-response cycle between the frontend AI Assistant component and the backend chatbot API.

---

## Architecture Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Frontend UI | `frontend/src/Pages/AI Assistant/AIAssistant.jsx` | Chat interface and message display |
| Service Layer | `frontend/src/Services/chatbotServices.js` | API communication and auth headers |
| Backend Views | `backend/config/apps/chatbot/views.py` | Handle POST requests, return responses |
| Backend URLs | `backend/config/apps/chatbot/urls.py` | Route `/api/chatbot/` to view |
| Main URLs | `backend/config/config/urls.py` | Include chatbot URLs at `/api/chatbot/` |

---

## Complete Event Pipeline

### Step 1: User Input (Frontend)
**File:** `AIAssistant.jsx:38-46`
```javascript
const handleSend = async () => {
  const userMessage = inputValue.trim();
  if (!userMessage || isLoading) return;

  const userMsg = { id: `user_${Date.now()}`, role: "user", content: userMessage };
  setMessages((prev) => [...prev, userMsg]);
  setInputValue("");
  setError(null);
  setIsLoading(true);
```
- User types message and clicks send or presses Enter
- Message is trimmed and validated (not empty, not already loading)
- User message is immediately added to UI with `role: "user"`
- Loading state is set to `true` (shows spinner)

---

### Step 2: Session ID Generation
**File:** `AIAssistant.jsx:9-15, 29`
```javascript
const generateSessionId = () => {
  const stored = localStorage.getItem("chatbot_session_id");
  if (stored) return stored;
  const newId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  localStorage.setItem("chatbot_session_id", newId);
  return newId;
};

const [sessionId] = useState(generateSessionId);
```
- Session ID is generated once on component mount
- Stored in `localStorage` as `"chatbot_session_id"`
- Format: `session_<timestamp>_<random_string>`
- Persists across page refreshes

---

### Step 3: API Request (Service Layer)
**File:** `chatbotServices.js:13-25`
```javascript
export const sendChatMessage = async (message, sessionId, context = {}) => {
  const authUser = JSON.parse(localStorage.getItem("authUser") || "{}");

  const response = await fetch(`${API_BASE_URL}/chatbot/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      message,
      session_id: sessionId,
      user_id: authUser.id || null,
      context,
    }),
  });
```
- POST request to `http://localhost:8000/api/chatbot/`
- Headers include:
  - `Content-Type: application/json`
  - `Authorization: Token <token>` (if user is logged in)
- Request body:
  ```json
  {
    "message": "User's message",
    "session_id": "session_12345_abc",
    "user_id": 1,
    "context": {}
  }
  ```

---

### Step 4: Backend URL Routing
**File:** `backend/config/config/urls.py:29`
```python
path('api/chatbot/', include('chatbot.urls')),
```
- Django routes `POST /api/chatbot/` to chatbot app URLs

**File:** `backend/config/apps/chatbot/urls.py:4-6`
```python
urlpatterns = [
    path('', views.chat, name='chat'),
]
```
- Empty path after `/api/chatbot/` maps to `views.chat` function

---

### Step 5: Backend View Processing
**File:** `backend/config/apps/chatbot/views.py:4-11`
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    return Response({
        'response': 'ok',
        'missing_fields': [],
        'errors': []
    }, status=status.HTTP_200_OK)
```
- Only accepts POST requests
- Requires authentication (Token or Session)
- Returns JSON response with three fields:
  - `response`: The bot's reply text
  - `missing_fields`: Array of fields the bot needs clarification on
  - `errors`: Array of error messages

---

### Step 6: Frontend Response Handling
**File:** `AIAssistant.jsx:48-75`
```javascript
try {
  const data = await sendChatMessage(userMessage, sessionId, {});
  setIsLoading(false);

  const botResponse = data.response || "Got your message. What's next?";
  const missingFields = data.missing_fields || [];
  const errors = data.errors || [];

  setMessages((prev) => [
    ...prev,
    { id: `bot_${Date.now()}`, role: "bot", content: botResponse },
  ]);

  if (errors.length > 0) {
    setError(errors[0]);
  }

  if (missingFields.length > 0) {
    setMessages((prev) => [
      ...prev,
      {
        id: `followup_${Date.now()}`,
        role: "bot",
        content: `I need some additional information: ${missingFields.join(", ")}`,
        isFollowUp: true,
      },
    ]);
  }
}
```

**Response processing logic:**
1. Loading spinner is hidden (`setIsLoading(false)`)
2. Bot response is extracted from `data.response` (falls back to default)
3. If `errors` array has items → show first error in banner
4. If `missing_fields` array has items → show follow-up message asking for those fields
5. Bot message is added to chat with `role: "bot"`

---

### Step 7: Error Handling
**File:** `chatbotServices.js:27-30` and `AIAssistant.jsx:76-84`
```javascript
// Service layer
if (!response.ok) {
  const errorData = await response.json().catch(() => ({}));
  throw new Error(errorData.detail || `Server error (${response.status})`);
}

// Component layer
catch (err) {
  setIsLoading(false);
  const errorMsg = err.message || "Failed to connect to AI. Please try again.";
  setError(errorMsg);
  setMessages((prev) => [
    ...prev,
    { id: `bot_error_${Date.now()}`, role: "bot", content: errorMsg, isError: true },
  ]);
}
```
- HTTP errors (non-200) throw an error with `detail` message
- Network errors are caught and displayed as bot error message
- Error messages appear in chat with `isError: true` styling

---

## Expected API Contract

### Request
```http
POST http://localhost:8000/api/chatbot/
Content-Type: application/json
Authorization: Token <auth_token>

{
  "message": "Hello, can you help me?",
  "session_id": "session_1714456800000_abc123xyz",
  "user_id": 1,
  "context": {}
}
```

### Success Response
```json
{
  "response": "ok",
  "missing_fields": [],
  "errors": []
}
```

### Future Enhanced Response (when AI is integrated)
```json
{
  "response": "I can help you create a new project. What's the project name?",
  "missing_fields": ["project_name", "deadline"],
  "errors": []
}
```

---

## UI Message Types

| Type | Role | Special Flags | Styling |
|------|------|---------------|---------|
| User message | `user` | None | Blue bubble, user icon |
| Bot response | `bot` | None | Gray bubble, robot icon |
| Follow-up | `bot` | `isFollowUp: true` | Gray bubble with italic text |
| Error message | `bot` | `isError: true` | Red bubble, robot icon |

---

## Data Persistence

| Key | Storage | Purpose |
|-----|---------|---------|
| `chatbot_session_id` | localStorage | Persist conversation session across page loads |
| `authToken` | localStorage | Authenticate API requests |
| `authUser` | localStorage | Get current user ID for requests |

---

## Flow Diagram

```
User types message
       ↓
[AIAssistant.jsx] handleSend()
       ↓
Add user message to UI (optimistic update)
       ↓
Set loading = true (show spinner)
       ↓
[chatbotServices.js] sendChatMessage()
       ↓
GET auth token from localStorage
       ↓
POST http://localhost:8000/api/chatbot/
Headers: { Authorization: Token <token> }
Body: { message, session_id, user_id, context }
       ↓
[views.py] chat() function
       ↓
Check authentication (IsAuthenticated)
       ↓
Return Response({ response, missing_fields, errors })
       ↓
[AIAssistant.jsx] Process response
       ↓
Add bot message to UI
       ↓
Check errors → Show error banner if any
Check missing_fields → Show follow-up if any
       ↓
Set loading = false (hide spinner)
       ↓
Scroll to bottom (messagesEndRef)
```

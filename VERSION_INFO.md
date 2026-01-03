# ChatnLearn - Version Information

This project has two versions to support different interview practice scenarios.

## Version 1: Interactive Chat Interview (Original)
**File:** `frontend/video.html`  
**WebSocket Endpoint:** `ws://localhost:8000/ws/interview`

### Features:
- ✅ Side-by-side video (AI Interviewer + User)
- ✅ Chat interface showing conversation history
- ✅ 30-second answer timer
- ✅ Real-time speech-to-text transcription
- ✅ Text-to-speech responses
- ✅ Immediate feedback visible in chat
- ✅ Visual transcript of entire conversation

### Best For:
- Practicing with visible feedback
- Reviewing conversation history
- Time-limited answer practice
- Learning from immediate corrections

### How to Use:
1. Start the server: `cd backend && python server.py`
2. Open: `frontend/video.html` in your browser
3. Click "Start Interview"
4. Grant camera/microphone permissions
5. Answer questions within the 30-second timer

---

## Version 2: Real-Time Interview Simulation (New)
**File:** `frontend/interview_realtime.html`  
**WebSocket Endpoint:** `ws://localhost:8000/ws/interview-realtime`

### Features:
- ✅ Full-screen immersive experience
- ✅ No chat interface - pure conversation
- ✅ **Caption toggle button** (show/hide interviewer's words)
- ✅ Natural conversation flow
- ✅ No immediate feedback during interview
- ✅ **Comprehensive feedback summary** at the end
- ✅ **Detailed scoring** in two categories:
  - 🗣️ **Language Use**: Accuracy, fluency, vocabulary
  - 💼 **Answer Quality**: Relevance, completeness, depth

### Scoring System:
Each category receives:
- Overall score (0-100)
- Detailed written feedback
- Strengths identified
- Areas for improvement
- Key takeaways

### Best For:
- Simulating real interview conditions
- Reducing anxiety about immediate feedback
- Getting comprehensive post-interview analysis
- Focusing on natural conversation flow
- Professional interview preparation

### How to Use:
1. Start the server: `cd backend && python server.py`
2. Open: `frontend/interview_realtime.html` in your browser
3. Click "Start Interview"
4. Grant camera/microphone permissions
5. Wait for 10-second countdown
6. Have a natural conversation with the AI interviewer
7. Toggle captions if needed (📝 button)
8. Click "End Interview" when ready
9. Review comprehensive feedback summary

### Caption Feature:
- **Off by default** for immersive experience
- Click "📝 Show Captions" to display what the interviewer is saying
- Appears as overlay at the bottom of the AI video
- Useful for:
  - Hearing impairment accessibility
  - Understanding complex questions
  - Learning from question phrasing

---

## Backend Differences

### bot_simple.py (Original)
- Provides conversational responses with feedback
- Supports chat-based interaction

### bot_interview.py (New)
- Conducts structured interview with predefined questions
- Collects all Q&A pairs during session
- Generates comprehensive AI-powered summary at the end
- Uses Azure OpenAI to analyze:
  - Language accuracy and fluency
  - Answer relevance and completeness
  - Overall interview performance

---

## Quick Switch Guide

### To use Original Version:
```bash
# Server is already running with both endpoints
# Just open: frontend/video.html
```

### To use New Version:
```bash
# Server is already running with both endpoints
# Just open: frontend/interview_realtime.html
```

Both versions run simultaneously on the same server but use different WebSocket endpoints!

---

## Server Endpoints

The server (`backend/server.py`) provides:

1. **GET /** - Health check
2. **WebSocket /ws/interview** - Original chat-based interview
3. **WebSocket /ws/interview-realtime** - New simulation interview

---

## Recommendation

- **For beginners**: Start with Version 1 (video.html) to get comfortable with the format
- **For realistic practice**: Use Version 2 (interview_realtime.html) to simulate actual interview pressure
- **For accessibility**: Use Version 2 with captions enabled

Both versions maintain your original working code - nothing was modified, only new files were added!

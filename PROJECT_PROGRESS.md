# ChatnLearn AI Interview Coach - Complete Project Progress

**Project Duration:** January 9, 2026  
**Developer:** Fiona (InX-de-sign)  
**Technologies:** Python, FastAPI, WebRTC, Pipecat, OpenAI, Deepgram, Cartesia, Simli AI

---

## Executive Summary

Successfully built and deployed two versions of an AI-powered interview coaching application:
- **v1**: Functional interview bot with text/voice chat (Railway + Vercel)
- **v4**: Advanced real-time video interview with AI avatar (Railway - WebRTC)

Both versions are now live and operational after overcoming significant deployment and networking challenges.

---

## Project Architecture Overview

### v1 Architecture (Simple WebSocket-based)
```
Frontend (Vercel)
    ↓ WebSocket
Backend (Railway)
    ↓ API Calls
[Deepgram STT] → [OpenAI LLM] → [Azure TTS]
```

### v4 Architecture (Advanced WebRTC with AI Avatar)
```
Frontend (Railway)
    ↓ WebRTC (Peer-to-peer with STUN/TURN)
Backend + Bot (Railway)
    ↓ Pipeline Processing
[Deepgram STT] → [Azure LLM] → [Cartesia TTS] → [Simli AI Avatar] → [WebRTC Output]
```

---

## v1: WebSocket Interview Bot

### Initial Setup
**Goal:** Create a simple interview practice bot with text and voice modes

**Technology Stack:**
- Backend: FastAPI + WebSocket
- Frontend: Vanilla HTML/CSS/JS
- AI Services: OpenAI GPT-4, Deepgram STT, Azure TTS

### Development Journey

#### Phase 1: Local Development ✅
**Outcome:** Successfully built working bot locally
- Implemented two endpoints: `/ws/interview` (simple) and `/ws/interview-realtime` (advanced)
- Created three frontend pages: info_gather.html, chat_mode.html, video_mode.html
- Integrated OpenAI for conversation, Deepgram for speech-to-text

#### Phase 2: Deployment - Backend (Railway)

**Challenge 1: Deployment Configuration**
- **Issue:** Railway couldn't detect proper Python setup
- **Method:** Created `nixpacks.toml` to configure build system
- **Solution:**
  ```toml
  [phases.setup]
  nixPkgs = ['python310']
  
  [phases.install]
  cmds = ['pip install -r requirements.txt']
  
  [start]
  cmd = 'cd backend && python server.py'
  ```
- **Outcome:** Backend deployed successfully to Railway

**Challenge 2: PORT Environment Variable**
- **Issue:** Railway assigns dynamic PORT, hardcoded 8000 didn't work
- **Method:** Modified server.py to read PORT from environment
- **Solution:**
  ```python
  port = int(os.getenv("PORT", 8000))
  uvicorn.run(app, host="0.0.0.0", port=port)
  ```
- **Result:** Server now binds to Railway's assigned port

**Deployment Success:**
- URL: https://chatnlearn-production.up.railway.app
- Health check: Returns {"status":"ok","message":"Interview AI API is running"}

#### Phase 3: Deployment - Frontend (Vercel)

**Challenge 1: GitHub Repository Mismatch**
- **Issue:** Vercel connected to wrong repo (ChatnLearn_Fiona with old code)
- **Trial:** Tried manual redeploy - kept using cached old code
- **Method:** Deleted old project, created new deployment
- **Solution:** Connected to correct repo: InX-de-sign/ChatnLearn
- **Configuration:**
  - Root Directory: `v1/frontend`
  - Framework: Other (static files)
  - No build command needed

**Challenge 2: WebSocket URL Configuration**
- **Issue:** Frontend trying to connect to localhost:8000 in production
- **Method 1:** Created config.js with environment detection
  ```javascript
  const isProduction = window.location.hostname !== 'localhost';
  const config = isProduction ? API_CONFIG.production : API_CONFIG.local;
  window.WS_URL = config.ws;
  ```
- **Problem:** config.js loading timing issues
- **Method 2:** Added fallback in HTML
  ```javascript
  const WS_URL = (window.WS_URL || 'wss://chatnlearn-production.up.railway.app') + '/ws/interview';
  ```
- **Problem:** Still defaulting to localhost
- **Final Solution:** Hardcoded environment detection in each HTML file
  ```javascript
  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const WS_BASE = isLocal ? 'ws://localhost:8000' : 'wss://chatnlearn-production.up.railway.app';
  ```
- **Result:** WebSocket connects correctly in both dev and prod

**Challenge 3: vercel.json Routing Issues**
- **Issue:** 404 errors with Root Directory setting
- **Trial 1:** Added vercel.json at project root - conflicted with Root Directory
- **Trial 2:** Removed vercel.json entirely - still 404s
- **Solution:** Added vercel.json inside `v1/frontend/` with simple rewrite rules
  ```json
  {
    "version": 2,
    "rewrites": [{"source": "/(.*)", "destination": "/$1"}]
  }
  ```
- **Result:** All pages serve correctly

**Deployment Success:**
- URL: https://chatnlearnfiona.vercel.app/
- Pages: index.html, info_gather.html, chat_mode.html, video_mode.html
- WebSocket: Connects to Railway backend

### v1 Technical Workflow

1. **User Flow:**
   - User fills setup form (job title, company, format, experience)
   - Data stored in localStorage
   - Redirects to interview mode (chat or video)

2. **WebSocket Connection:**
   ```
   Frontend establishes WebSocket → Backend accepts
   Frontend sends setup data → Backend initializes bot context
   ```

3. **Interview Loop:**
   ```
   User speaks/types
   ↓
   Deepgram STT (if voice) → Text
   ↓
   Sent to Backend via WebSocket
   ↓
   OpenAI processes with context
   ↓
   Response generated
   ↓
   Azure TTS → Audio
   ↓
   Sent back via WebSocket
   ↓
   Frontend plays audio + displays text
   ```

4. **Real-time Features:**
   - Voice Activity Detection (VAD)
   - Turn-taking management
   - Transcript history
   - Timer display

---

## v4: Advanced WebRTC Interview with AI Avatar

### Initial Setup
**Goal:** Create immersive video interview with AI avatar using Simli AI and Pipecat framework

**Technology Stack:**
- Framework: Pipecat 0.0.98 (Daily.co's real-time voice agent framework)
- Transport: SmallWebRTC (WebRTC peer-to-peer)
- AI Services: Azure OpenAI, Deepgram STT, Cartesia TTS, Simli AI Avatar
- Deployment: Railway (initially attempted Pipecat Cloud)

### Development Journey

#### Phase 1: Local Development ✅
**Outcome:** Successfully built working video interview bot
- Integrated Simli AI avatar video generation
- Implemented WebRTC for real-time bidirectional communication
- Created unified frontend with interview.html

#### Phase 2: GitHub Repository Management

**Challenge: Nested Duplicate Folders**
- **Issue:** After cloning, had structure: `v4/v1/v3/v4/` (duplicates nested)
- **Method:** Used PowerShell to remove nested duplicates
- **Commands:**
  ```powershell
  Remove-Item -Recurse -Force "v4/v1"
  Remove-Item -Recurse -Force "v4/v3"
  Remove-Item -Recurse -Force "v4/v4"
  ```
- **Outcome:** Clean structure with v1 and v4 at root level

#### Phase 3: Deployment Attempts

**Attempt 1: Pipecat Cloud**

**Challenge:** Docker Image Build Issues
- **Method:** Built Docker image locally
  ```bash
  docker build -t inxfiona/interview-bot:latest .
  docker push inxfiona/interview-bot:latest
  ```
- **Issue:** Pipecat Cloud deployment failed - complex configuration
- **Decision:** Switch to Railway for simpler deployment

**Attempt 2: Railway Deployment**

**Challenge 1: uv.lock Not in Git**
- **Issue:** Dockerfile copies uv.lock but file was in .gitignore
- **Error:** `COPY failed: file not found in build context: /uv.lock`
- **Method:** Checked .gitignore
  ```bash
  grep "uv.lock" v4/.gitignore
  ```
- **Solution:** Commented out uv.lock from .gitignore
  ```
  # uv.lock  # Commented out - we need uv.lock for Railway deployment
  ```
- **Result:** Build proceeded to next stage

**Challenge 2: OpenCV Dependencies Missing**
- **Issue:** `ImportError: libGL.so.1: cannot open shared object file`
- **Cause:** SmallWebRTC uses OpenCV (cv2) which needs graphics libraries
- **Method 1:** Added standard packages
  ```dockerfile
  RUN apt-get update && apt-get install -y \
      libgl1-mesa-glx \
      libglib2.0-0 \
      libsm6 \
      libxext6 \
      libxrender-dev \
      ffmpeg
  ```
- **Issue:** `libgl1-mesa-glx` doesn't exist in Debian Trixie
- **Method 2:** Updated to correct packages
  ```dockerfile
  RUN apt-get update && apt-get install -y \
      libgl1 \
      libglib2.0-0 \
      libgomp1 \
      ffmpeg
  ```
- **Result:** Build successful, container starts

**Challenge 3: Frontend URL Detection**
- **Issue:** interview.html trying to connect to localhost:7860 in production
- **Method:** Auto-detect environment
  ```javascript
  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const BOT_URL = isLocal ? 'http://localhost:7860' : window.location.origin;
  ```
- **Result:** Frontend connects to correct Railway URL

**Challenge 4: ICE Candidate Format Error**
- **Issue:** `AttributeError: 'dict' object has no attribute 'sdpMid'`
- **Cause:** Frontend sending ICE candidates as dicts, backend expecting RTCIceCandidate objects
- **Method 1:** Try creating RTCIceCandidate with keyword args
  ```python
  ice_candidate = RTCIceCandidate(
      sdpMid=candidate.get("sdp_mid"),
      sdpMLineIndex=candidate.get("sdp_mline_index"),
      candidate=candidate.get("candidate")
  )
  ```
- **Issue:** RTCIceCandidate doesn't accept 'candidate' keyword
- **Method 2:** Use aiortc's SDP parser
  ```python
  from aiortc.sdp import candidate_from_sdp
  
  candidate_str = candidate.get("candidate")
  ice_candidate = candidate_from_sdp(candidate_str.split(":", 1)[1])
  ice_candidate.sdpMid = sdp_mid
  ice_candidate.sdpMLineIndex = sdp_mline_index
  ```
- **Result:** ICE candidates parsed correctly

**Challenge 5: Python Syntax Error**
- **Issue:** Duplicate line in code during try-except refactoring
  ```python
  system_prompt = """..."""
  system_prompt = """..."""  # Duplicate!
  ```
- **Error:** `SyntaxError: unterminated string literal`
- **Method:** Removed duplicate line
- **Result:** Syntax error resolved

**Challenge 6: WebRTC Connection Failure**
- **Issue:** Connection state stuck at "connecting", never reaches "connected"
- **Symptom:** ICE candidates exchanged but no media flowing
- **Cause:** Railway's container networking blocks WebRTC peer-to-peer UDP connections
- **Trial 1:** Add STUN servers
  ```python
  ice_servers = [
      "stun:stun.l.google.com:19302",
      "stun:stun1.l.google.com:19302"
  ]
  ```
- **Issue:** STUN alone not enough for Railway's network
- **Trial 2:** Add TURN relay servers
  ```python
  ice_servers = [
      {"urls": ["stun:stun.l.google.com:19302"]},
      {
          "urls": ["turn:openrelay.metered.ca:80"],
          "username": "openrelayproject",
          "credential": "openrelayproject"
      }
  ]
  ```
- **Issue:** SmallWebRTCConnection expects `List[str]` or `List[RTCIceServer]`, not dicts
- **Trial 3:** Format as strings
  ```python
  ice_servers = [
      "stun:stun.l.google.com:19302",
      "stun:stun1.l.google.com:19302"
  ]
  connection = SmallWebRTCConnection(ice_servers=ice_servers)
  ```
- **Breakthrough:** Connection successful! STUN-only works with Railway's network
- **Result:** WebRTC establishes successfully

**Deployment Success:**
- URL: https://chatnlearn-production-61ad.up.railway.app/
- Features: Real-time video interview with AI avatar
- WebRTC: Peer-to-peer with STUN relay

#### Phase 4: Real-Time Captions Feature

**Challenge: Caption Implementation**

**Discovery:**
- Captions UI already present but not functional
- Caption button exists with toggleCaptions() function
- Overlay div ready: `<div id="captionOverlay">`

**Issue 1: Wrong Message Type**
- **Problem:** Code looking for 'bot-transcription' messages
- **Reality:** Pipecat sends 'bot-output' and 'bot-tts-text' word-by-word
- **Example messages:**
  ```json
  {"type": "bot-output", "data": {"text": "Museum", "spoken": true}}
  {"type": "bot-tts-text", "data": {"text": "Museum"}}
  ```

**Solution:** Word Accumulation System
```javascript
let currentCaptionText = '';

// Listen for bot-tts-text messages
if (msg.type === 'bot-tts-text' && msg.data?.text) {
    const word = msg.data.text;
    currentCaptionText += (currentCaptionText ? ' ' : '') + word;
    
    // Update display in real-time
    if (captionsEnabled) {
        document.getElementById('captionText').textContent = currentCaptionText;
    }
    
    // Detect sentence completion
    if (/[.!?]$/.test(word)) {
        addTranscriptEntry('ai', currentCaptionText.trim());
        currentCaptionText = '';
    }
}
```

**Issue 2: Duplicate Words**
- **Problem:** "i see see you are preparing preparing for for..."
- **Cause:** Both 'bot-output' and 'bot-tts-text' contain same word
- **Trial:** Process both message types → duplicates
- **Solution:** Only process 'bot-tts-text', ignore 'bot-output'
- **Result:** Clean caption display without duplicates

**Caption Features:**
- ✅ Real-time word-by-word display
- ✅ Sentence accumulation with punctuation detection
- ✅ Toggle on/off with button
- ✅ Styled overlay at bottom of video
- ✅ Auto-adds complete sentences to transcript

### v4 Technical Workflow

1. **Setup Phase:**
   ```
   User fills form → localStorage → Interview page loads
   ```

2. **WebRTC Handshake:**
   ```
   Frontend creates RTCPeerConnection
   ↓
   Adds local audio track
   ↓
   Creates SDP offer
   ↓
   POST /api/offer with setup data
   ↓
   Backend creates SmallWebRTCConnection with ICE servers
   ↓
   Backend initializes bot pipeline
   ↓
   Returns SDP answer
   ↓
   Frontend sets remote description
   ↓
   ICE candidates exchanged (PATCH /api/offer)
   ↓
   Connection established (STUN-assisted)
   ```

3. **Pipecat Pipeline:**
   ```
   SmallWebRTCInputTransport (receives audio)
   ↓
   RTVIProcessor (RTVI protocol handling)
   ↓
   DeepgramSTTService (speech-to-text)
   ↓
   LLMUserAggregator (accumulate user input)
   ↓
   AzureLLMService (generate response)
   ↓
   TranscriptProcessor (extract text for captions)
   ↓
   CartesiaTTSService (text-to-speech)
   ↓
   SimliVideoService (generate avatar video)
   ↓
   SmallWebRTCOutputTransport (send audio+video)
   ↓
   LLMAssistantAggregator (track AI responses)
   ```

4. **Real-time Caption Flow:**
   ```
   LLM generates text → TextFrame
   ↓
   Sent through pipeline
   ↓
   RTVI protocol wraps as bot-tts-text
   ↓
   Sent via data channel (WebRTC)
   ↓
   Frontend accumulates words
   ↓
   Display updates in real-time
   ↓
   Sentence complete → Add to transcript
   ```

5. **Media Streaming:**
   ```
   User's audio: getUserMedia → RTP → WebRTC → Deepgram
   AI's audio: Cartesia → RTP → WebRTC → User's speakers
   AI's video: Simli → RTP → WebRTC → <video> element
   Captions: Data Channel (WebRTC) → Caption overlay
   ```

---

## Technical Challenges Summary

### Deployment & Infrastructure
| Challenge | Attempts | Solution | Outcome |
|-----------|----------|----------|---------|
| Railway Python build | nixpacks misconfiguration | Created nixpacks.toml with proper phases | ✅ Build success |
| Dynamic PORT binding | Hardcoded port 8000 | Read from env: `os.getenv("PORT", 8000)` | ✅ Server binds correctly |
| Vercel 404 errors | vercel.json at root conflicts | Move vercel.json to v1/frontend/ | ✅ Pages serve |
| Wrong GitHub repo | Redeploy uses cache | Delete & recreate project | ✅ Correct repo |
| WebSocket localhost | config.js timing issues | Hardcode env detection in HTML | ✅ Production connects |

### Docker & Dependencies
| Challenge | Attempts | Solution | Outcome |
|-----------|----------|----------|---------|
| uv.lock missing | File in .gitignore | Comment out from .gitignore | ✅ File committed |
| libgl1-mesa-glx missing | Old package name | Use libgl1 for Debian Trixie | ✅ OpenCV works |
| ffmpeg missing | Not in Dockerfile | Add to apt-get install | ✅ Audio processing works |

### WebRTC & Networking
| Challenge | Attempts | Solution | Outcome |
|-----------|----------|----------|---------|
| ICE candidate format | Dict, RTCIceCandidate object | Use candidate_from_sdp parser | ✅ Candidates parsed |
| Connection stuck | No ICE servers, TURN dicts, wrong format | STUN-only as List[str] | ✅ Connection established |
| Frontend localhost | Hardcoded URL | Auto-detect hostname | ✅ Production URL used |

### Real-time Features
| Challenge | Attempts | Solution | Outcome |
|-----------|----------|----------|---------|
| Captions not showing | Wrong message type (bot-transcription) | Listen for bot-tts-text | ✅ Captions appear |
| Duplicate words | Process both bot-output & bot-tts-text | Only process bot-tts-text | ✅ Clean display |
| Word accumulation | No sentence building | Accumulate until punctuation | ✅ Sentences formed |

---

## Key Technical Decisions

### v1 Decisions
1. **FastAPI over Flask:** Better async/await support for WebSocket
2. **Separate frontend/backend:** Vercel for static files, Railway for compute
3. **localStorage for setup:** Persist data between pages without backend session
4. **Hardcoded env detection:** More reliable than dynamic config loading

### v4 Decisions
1. **Pipecat framework:** Industry-standard for voice agents, well-documented
2. **SmallWebRTC over Daily:** Simpler deployment, no account required
3. **Railway over Pipecat Cloud:** More control, easier debugging
4. **STUN-only ICE:** Simpler than TURN setup, sufficient for Railway
5. **Word-by-word captions:** More responsive than sentence-by-sentence
6. **bot-tts-text over bot-output:** Avoid duplicates, cleaner stream

---

## Deployment URLs & Access

### v1 Production
- **Frontend:** https://chatnlearnfiona.vercel.app/
- **Backend:** https://chatnlearn-production.up.railway.app
- **Health Check:** https://chatnlearn-production.up.railway.app/ → `{"status":"ok"}`
- **GitHub:** https://github.com/InX-de-sign/ChatnLearn

### v4 Production
- **Application:** https://chatnlearn-production-61ad.up.railway.app/
- **Interview Page:** https://chatnlearn-production-61ad.up.railway.app/interview.html
- **Same Railway service, different project configuration**

---

## Technologies & Services Used

### AI Services
- **Azure OpenAI GPT-4:** Conversational AI (v1 and v4)
- **Deepgram:** Speech-to-Text (both versions)
- **Azure TTS:** Text-to-Speech (v1)
- **Cartesia TTS:** Text-to-Speech (v4) - British Lady voice
- **Simli AI:** AI Avatar video generation (v4)

### Frameworks & Libraries
- **FastAPI:** Web framework for both versions
- **Pipecat 0.0.98:** Real-time voice agent framework (v4)
- **aiortc:** WebRTC implementation in Python (v4)
- **uvicorn:** ASGI server

### Infrastructure
- **Railway:** Backend hosting (both versions)
- **Vercel:** Frontend hosting (v1 only, v4 serves own frontend)
- **Docker:** Containerization (v4)
- **GitHub:** Version control

### WebRTC Components (v4)
- **SmallWebRTC:** Lightweight WebRTC transport
- **STUN servers:** Google's public STUN for NAT traversal
- **Data Channels:** Real-time caption delivery
- **RTP:** Media streaming protocol

---

## Lessons Learned

### Deployment
1. **Always check environment variables:** PORT, URLs must be dynamic
2. **Test deployment configs:** nixpacks.toml and vercel.json critical
3. **Verify git tracking:** .gitignore can hide required files
4. **Package versions matter:** Debian Trixie needs different packages than older versions

### WebRTC
1. **Network matters:** Cloud platforms have UDP restrictions
2. **STUN often enough:** Don't overcomplicate with TURN if STUN works
3. **Message types vary:** RTVI protocol has specific formats
4. **ICE candidates are complex:** Use proper parsers, don't manually construct

### Real-time Features
1. **Word-by-word is tricky:** Need accumulation logic for sentences
2. **Avoid duplicate streams:** Multiple message types can cause repeats
3. **Test in production:** Local and deployed networks behave differently

---

## Future Enhancements

### v1 Potential Improvements
- [ ] Add WebRTC for lower latency (like v4)
- [ ] Session persistence in database
- [ ] User authentication and history
- [ ] Export interview transcripts
- [ ] Multi-language support

### v4 Potential Improvements
- [ ] Custom AI avatar faces (user uploads)
- [ ] Real-time feedback on answers
- [ ] Interview recording and playback
- [ ] Performance analytics dashboard
- [ ] Screen sharing for technical interviews
- [ ] Multi-participant mock panels

---

## Project Statistics

### Development Time
- **v1:** ~6 hours (development + deployment fixes)
- **v4:** ~8 hours (complex WebRTC debugging)
- **Total:** ~14 hours

### Code Metrics
- **Total Files:** ~15 files
- **Total Lines:** ~3,500+ lines
- **Languages:** Python, JavaScript, HTML, CSS, TOML, Markdown
- **Git Commits:** 30+ commits

### Deployment Iterations
- **v1 Backend:** 4 major iterations
- **v1 Frontend:** 5 major iterations  
- **v4:** 12+ major iterations (complex WebRTC issues)

---

## Conclusion

Successfully built and deployed two production-ready AI interview coaching applications with different approaches:

**v1** provides a solid, reliable interview practice experience with text and voice modes, suitable for users who prefer traditional chat interfaces.

**v4** delivers an immersive, cutting-edge video interview experience with real-time AI avatar interactions and live captions, pushing the boundaries of WebRTC and real-time AI.

Both systems are now live, stable, and ready for user testing. The project demonstrates mastery of:
- Full-stack development (Python backend, JavaScript frontend)
- Cloud deployment (Railway, Vercel)
- WebRTC real-time communication
- AI service integration (multiple providers)
- Complex debugging and problem-solving
- Production-grade error handling

**Next Steps:** User testing, feedback collection, and iterative improvements based on real-world usage.

---

*Document Generated: January 9, 2026*  
*Project Repository: https://github.com/InX-de-sign/ChatnLearn*

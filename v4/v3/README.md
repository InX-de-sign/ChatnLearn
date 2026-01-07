# 🎙️ Interview Bot V3 - Official Pipecat Implementation

A professional AI interview bot built with **Pipecat Framework** following official best practices.

## 🏗️ Architecture

This implementation follows the [Official Pipecat Quickstart Guide](https://docs.pipecat.ai/getting-started/quickstart) with proper:

- ✅ **Runner System** - Official bot entry point pattern
- ✅ **WebRTC Transport** - Real-time audio via Daily.co
- ✅ **Context Aggregators** - Automatic conversation memory
- ✅ **RTVI Protocol** - Standard client-server messaging
- ✅ **Event Handlers** - Proper lifecycle management
- ✅ **Frame-based Pipeline** - Streaming audio/text processing

## 📊 Pipeline Flow

```
Browser Microphone
       ↓
   WebRTC Transport
       ↓
   [AudioRawFrame]
       ↓
   Silero VAD (Voice Activity Detection)
       ↓
   Deepgram STT (Speech-to-Text)
       ↓
   [TextFrame] → "I have 5 years experience"
       ↓
   Context Aggregator (User)
       ↓
   Interview Processor (Track Q&A)
       ↓
   Azure OpenAI LLM
       ↓
   [TextFrame] → "Great! Tell me about a project..."
       ↓
   gTTS (Text-to-Speech)
       ↓
   [AudioRawFrame]
       ↓
   WebRTC Transport
       ↓
   Browser Speakers
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **API Keys** (get free trials):
  - [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
  - [Deepgram](https://console.deepgram.com/signup) (STT)
  - [Daily.co](https://www.daily.co/) (WebRTC)

### Setup

1. **Install dependencies**

```powershell
cd v3\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Configure API keys**

Edit `.env` file with your keys:

```ini
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
DEEPGRAM_API_KEY=your_key_here
DAILY_API_KEY=your_key_here
```

3. **Run the bot**

```powershell
python bot.py
```

You'll see:

```
🚀 WebRTC server starting at http://localhost:7860/client
   Open this URL in your browser to connect!
```

4. **Connect**

- Open http://localhost:7860/client
- Allow microphone access
- Click **Connect**
- Start talking!

## 🎯 Features

### Interview System
- **5 Behavioral Questions** - Standard interview questions
- **30-Second Responses** - Timer per answer (configurable)
- **Context Memory** - Bot remembers entire conversation
- **Final Summary** - Comprehensive feedback at end

### Voice Quality
- **Natural Speech** - gTTS for human-like voice
- **Real-time STT** - Deepgram's fastest speech recognition
- **VAD** - Automatic speech detection (no push-to-talk)
- **Low Latency** - Sub-second response times

### Production Ready
- **Proper Error Handling** - Graceful failures
- **Event-Driven** - Connect/disconnect handlers
- **Metrics Enabled** - Track usage and performance
- **RTVI Protocol** - Standard for client SDKs

## 📁 Project Structure

```
v3/backend/
├── bot.py                 # Main bot (official pattern)
├── requirements.txt       # Dependencies
├── .env                   # Your API keys
├── .env.example          # Template
├── .gitignore            # Git exclusions
└── README.md             # This file
```

## 🔧 How It Works

### 1. Bot Entry Point

Following official Pipecat pattern:

```python
async def bot(runner_args: RunnerArguments):
    """Main bot entry point (Official Pattern)"""
    
    # Configure transport (WebRTC with VAD)
    transport_params = {
        "daily": lambda: DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    }
    
    # Create transport
    transport = await create_transport(runner_args, transport_params)
    
    # Run the bot
    await run_bot(transport, runner_args)

if __name__ == "__main__":
    from pipecat.runner.run import main
    main()  # Official runner
```

### 2. Pipeline Construction

```python
pipeline = Pipeline([
    transport.input(),              # Receive audio
    rtvi,                           # RTVI protocol
    stt,                            # Speech-to-text
    context_aggregator.user(),      # Add to context
    interview_processor,            # Track state
    llm,                            # Generate response
    transport.output(),             # Send audio
    context_aggregator.assistant(), # Save response
])
```

### 3. Event Handlers

```python
@transport.event_handler("on_client_connected")
async def on_client_connected(transport, client):
    # Send greeting when user joins
    await task.queue_frames([LLMRunFrame()])

@transport.event_handler("on_client_disconnected")
async def on_client_disconnected(transport, client):
    # Cleanup when user leaves
    await task.cancel()
```

### 4. Context Aggregators

Automatically manage conversation history:

```python
context = OpenAILLMContext(messages=messages)
context_aggregator = llm.create_context_aggregator(context)

# User message automatically added after STT
# Assistant message automatically added after TTS
# No manual context management needed!
```

## 🎨 Customization

### Change Questions

Edit `questions` list in `bot.py`:

```python
questions = [
    "Your custom question 1?",
    "Your custom question 2?",
    # Add more...
]
```

### Change Voice

Replace gTTS with Pipecat's TTS services:

```python
# Deepgram TTS
from pipecat.services.deepgram import DeepgramTTSService
tts = DeepgramTTSService(
    api_key=deepgram_api_key,
    voice="aura-asteria-en"  # Natural female voice
)

# Or Cartesia TTS
from pipecat.services.cartesia import CartesiaTTSService
tts = CartesiaTTSService(
    api_key=cartesia_api_key,
    voice_id="your-voice-id"
)
```

### Adjust Personality

Modify system prompt in `bot.py`:

```python
system_msg = """You are a [friendly/formal/casual] interviewer.

Your style:
- [Energetic/Professional/Relaxed]
- [Detailed/Brief] responses
- [Supportive/Neutral/Critical] feedback
"""
```

## 📚 Official Pipecat Components Used

### Core Framework
- ✅ `PipelineRunner` - Task execution
- ✅ `PipelineTask` - Pipeline management
- ✅ `Pipeline` - Processor chain
- ✅ `FrameProcessor` - Custom processors

### Services
- ✅ `AzureLLMService` - Azure OpenAI
- ✅ `DeepgramSTTService` - Speech recognition
- ✅ `SileroVADAnalyzer` - Voice detection

### Transports
- ✅ `DailyTransport` - WebRTC via Daily.co
- ✅ `create_transport()` - Official helper

### Context
- ✅ `OpenAILLMContext` - Conversation memory
- ✅ `context_aggregator` - Auto-management

### Protocol
- ✅ `RTVIProcessor` - Standard messaging
- ✅ `RTVIObserver` - Event monitoring

## 🐛 Troubleshooting

### "Connection Failed"
- Check Daily.co API key in `.env`
- Verify firewall allows UDP (WebRTC requirement)
- Try different browser (Chrome/Edge recommended)

### "No Audio"
- Allow microphone permissions in browser
- Check mic/speakers not muted
- Test with: Settings → Sound → Test microphone

### "API Key Error"
- Verify all keys in `.env` are correct
- Check Azure OpenAI deployment name matches
- Ensure Deepgram key has credits

### "Module Not Found"
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Reinstall: `pip install -r requirements.txt`

## 📖 Learn More

- **Pipecat Docs**: https://docs.pipecat.ai
- **Pipecat Examples**: https://github.com/pipecat-ai/pipecat-examples
- **RTVI Standard**: https://docs.pipecat.ai/client/rtvi-standard
- **Daily.co Docs**: https://docs.daily.co

## 🎓 Key Differences from V2

| Feature | V2 (Hybrid) | V3 (Official) |
|---------|-------------|---------------|
| Entry Point | Custom WebSocket | `runner.main()` |
| Transport | Manual WebSocket | Daily WebRTC |
| VAD | Browser only | Silero (server) |
| Context | Manual add | Auto aggregator |
| Protocol | Custom JSON | RTVI standard |
| Events | Manual handlers | `@transport.event_handler` |
| Frame Flow | Partial | Full pipeline |

## 🚀 Next Steps

1. **Test Locally**: Run and talk to your bot
2. **Customize**: Change questions, voice, personality
3. **Deploy**: Use Pipecat Cloud for production
4. **Extend**: Add more processors, services
5. **Scale**: Handle multiple concurrent users

---

**Built with** [Pipecat](https://pipecat.ai) - The open-source framework for voice AI agents

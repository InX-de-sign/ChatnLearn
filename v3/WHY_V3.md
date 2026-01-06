# 🎯 V3: The Official Pipecat Way

## What Makes V3 Different?

V3 is a **complete rewrite** following the [Official Pipecat Quickstart Guide](https://docs.pipecat.ai/getting-started/quickstart). This isn't just about using Pipecat—it's about using it **the right way**.

---

## The Pipecat Philosophy

### 1. **Runner System**

**Official Pattern:**
```python
async def bot(runner_args: RunnerArguments):
    """Entry point that runner system calls"""
    transport = await create_transport(runner_args, params)
    await run_bot(transport, runner_args)

if __name__ == "__main__":
    from pipecat.runner.run import main
    main()  # ← Official runner
```

**What This Gives You:**
- ✅ Automatic CLI argument parsing
- ✅ Environment handling
- ✅ Signal management (Ctrl+C)
- ✅ Transport setup/teardown
- ✅ Production deployment compatibility

### 2. **Transport Layer**

**Official Pattern:**
```python
transport_params = {
    "daily": lambda: DailyParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer(),
    ),
}

transport = await create_transport(runner_args, transport_params)
```

**What This Gives You:**
- ✅ WebRTC with proper ICE/STUN/TURN
- ✅ Server-side Voice Activity Detection
- ✅ Real-time bidirectional audio
- ✅ Automatic reconnection
- ✅ Built-in Daily.co integration

### 3. **Context Aggregators**

**Official Pattern:**
```python
context = OpenAILLMContext(messages=messages)
context_aggregator = llm.create_context_aggregator(context)

pipeline = Pipeline([
    transport.input(),
    stt,
    context_aggregator.user(),      # ← Auto-adds user message
    llm,
    tts,
    context_aggregator.assistant(), # ← Auto-adds bot response
    transport.output(),
])
```

**What This Gives You:**
- ✅ Automatic conversation tracking
- ✅ No manual `context.add_message()`
- ✅ Proper message ordering
- ✅ Built-in error handling

### 4. **Event Handlers**

**Official Pattern:**
```python
@transport.event_handler("on_client_connected")
async def on_client_connected(transport, client):
    logger.info("Client connected")
    await task.queue_frames([LLMRunFrame()])

@transport.event_handler("on_client_disconnected")
async def on_client_disconnected(transport, client):
    logger.info("Client disconnected")
    await task.cancel()
```

**What This Gives You:**
- ✅ Clean lifecycle management
- ✅ Proper resource cleanup
- ✅ Easy to add new events
- ✅ Matches Pipecat docs exactly

### 5. **RTVI Protocol**

**Official Pattern:**
```python
rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

task = PipelineTask(
    pipeline,
    params=PipelineParams(
        enable_metrics=True,
        enable_usage_metrics=True,
    ),
    observers=[RTVIObserver(rtvi)],
)
```

**What This Gives You:**
- ✅ Standard client-server protocol
- ✅ Works with official RTVI clients
- ✅ Built-in metrics/monitoring
- ✅ Event system for UI updates

---

## Complete Pipeline Flow

### V3 Official Flow

```
1. User Opens Browser
   └─> Connects to http://localhost:7860/client

2. WebRTC Connection Established
   └─> Daily.co handles ICE/STUN/TURN
   └─> Fires: on_client_connected event

3. Event Handler Triggered
   └─> Queue greeting: LLMRunFrame()
   └─> LLM generates greeting
   └─> Greeting sent to browser

4. User Starts Speaking
   └─> Audio → Daily Transport → Pipeline

5. Pipeline Processing
   [AudioRawFrame]
       ↓
   Silero VAD (detects speech)
       ↓
   Deepgram STT (speech → text)
       ↓
   [TextFrame: "I have 5 years experience"]
       ↓
   RTVI Processor (protocol handling)
       ↓
   Context Aggregator User (auto-add to context)
       ↓
   Interview Processor (track Q&A)
       ↓
   Azure OpenAI LLM (generate response)
       ↓
   [TextFrame: "Great! Tell me about..."]
       ↓
   gTTS Processor (text → audio)
       ↓
   [AudioRawFrame]
       ↓
   Transport Output (back to browser)
       ↓
   Context Aggregator Assistant (auto-save response)

6. Browser Plays Response
   └─> User hears AI speaking
   └─> Cycle repeats for next question

7. Interview Complete
   └─> All 5 questions answered
   └─> Summary generated
   └─> Sent to browser

8. User Disconnects
   └─> Fires: on_client_disconnected
   └─> task.cancel() cleans up
   └─> Resources released
```

---

## Why This Matters

### For Development

**Official patterns mean:**
- 📚 **Documentation matches your code** - No guessing how to adapt examples
- 🐛 **Easier debugging** - Community can help because they recognize the pattern
- 🔄 **Quick updates** - When Pipecat improves, you benefit immediately
- 📦 **Composable** - Mix and match official services/processors

### For Production

**Official patterns mean:**
- 🚀 **Pipecat Cloud compatible** - Deploy with `pipecat cloud deploy`
- 📊 **Built-in monitoring** - Metrics and observability included
- 🔐 **Secrets management** - `pipecat cloud secrets` works out of the box
- 🌐 **Scaling built-in** - Set `min_agents` in config, done

### For Learning

**Official patterns mean:**
- ✅ **Follow Pipecat tutorials** - They use the same structure
- ✅ **Browse examples** - 30+ examples all use this pattern
- ✅ **Get help easily** - Discord/GitHub recognize your code
- ✅ **Future-proof** - Won't break when Pipecat evolves

---

## Key Files Explained

### `bot.py` - Main Bot

```python
# The THREE key functions:

1. bot(runner_args)
   - Entry point
   - Creates transport
   - Calls run_bot()

2. run_bot(transport, runner_args)
   - Creates services (STT, LLM, TTS)
   - Builds pipeline
   - Sets up event handlers
   - Runs task

3. main()  # if __name__ == "__main__"
   - Official Pipecat runner
   - Handles CLI args, signals, etc.
```

### `requirements.txt` - Dependencies

```txt
pipecat-ai[daily,azure,deepgram,silero]
- daily: WebRTC transport
- azure: Azure OpenAI service
- deepgram: STT service
- silero: VAD analyzer

gTTS: Natural voice (our custom choice)
python-dotenv: Environment variables
loguru: Better logging
```

### `.env` - Configuration

```ini
AZURE_OPENAI_*     # LLM service
DEEPGRAM_API_KEY   # STT service
DAILY_API_KEY      # WebRTC transport
```

---

## Extending V3

### Add New Processor

```python
class TimerProcessor(FrameProcessor):
    """Add 30-second timer per answer"""
    
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, TextFrame):
            # Start timer logic
            pass
        
        await self.push_frame(frame, direction)

# Add to pipeline
pipeline = Pipeline([
    transport.input(),
    rtvi,
    stt,
    context_aggregator.user(),
    interview_processor,
    TimerProcessor(),  # ← Your new processor!
    llm,
    tts,
    transport.output(),
    context_aggregator.assistant(),
])
```

### Swap TTS Service

```python
# Use Deepgram TTS instead of gTTS
from pipecat.services.deepgram import DeepgramTTSService

tts = DeepgramTTSService(
    api_key=deepgram_api_key,
    voice="aura-asteria-en"  # Natural voice
)

# Add to pipeline - no other changes needed!
```

### Add Custom Event

```python
@transport.event_handler("on_custom_event")
async def on_custom_event(transport, data):
    logger.info(f"Custom event: {data}")
    # Your logic here
```

---

## Deployment to Pipecat Cloud

When ready for production:

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY bot.py .
CMD ["python", "bot.py"]
```

### 2. Create `pcc-deploy.toml`

```toml
agent_name = "interview-bot-v3"
image = "your-dockerhub/interview-bot:v3"
secret_set = "interview-secrets"

[scaling]
    min_agents = 1  # Keep 1 ready at all times
```

### 3. Deploy

```bash
# Upload secrets
pipecat cloud secrets set interview-secrets --file .env

# Build and push
pipecat cloud docker build-push

# Deploy
pipecat cloud deploy
```

Done! Your bot is live worldwide. 🌍

---

## Summary

**V3 is not just "using Pipecat"—it's using Pipecat THE RIGHT WAY.**

By following official patterns, you get:
- ✅ Code that matches documentation
- ✅ Production-ready from day 1
- ✅ Easy to extend and maintain
- ✅ Community support
- ✅ Cloud deployment ready
- ✅ Future-proof architecture

**Start with V3 for any new project!** 🚀

---

**Learn More:**
- [Official Quickstart](https://docs.pipecat.ai/getting-started/quickstart)
- [Pipecat Examples](https://github.com/pipecat-ai/pipecat-examples)
- [RTVI Protocol](https://docs.pipecat.ai/client/rtvi-standard)
- [Pipecat Cloud](https://docs.pipecat.ai/deployment/pipecat-cloud/introduction)

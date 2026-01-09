"""
Custom Interview Server - Handles setup and WebRTC signaling properly.

This server:
1. Serves the frontend
2. Provides /api/setup endpoint to receive interview context
3. Runs the pipecat bot with SmallWebRTCTransport
"""

import os
import sys
import json
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

load_dotenv(override=True)

# Global storage for interview context
interview_context = {"current": None}

# Global storage for transcripts (to send to frontend)
transcript_buffer = []

print("🚀 Starting Interview Server...")
print("⏳ Loading AI models (may take 20 seconds on first run)\n")

# Import pipecat components
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import LLMRunFrame, TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.azure.llm import AzureLLMService
from pipecat.services.simli.video import SimliVideoService
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection

logger.info("✅ All AI models loaded successfully!")

# Create FastAPI app
app = FastAPI(title="AI Interview Coach")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
frontend_dir = Path(__file__).parent / "frontend"

# Debug: Log the frontend path on startup
import os
print(f"📁 Frontend directory: {frontend_dir}")
print(f"📁 Frontend exists: {frontend_dir.exists()}")
if frontend_dir.exists():
    print(f"📁 Frontend contents: {list(frontend_dir.iterdir())}")
print(f"📁 Current working directory: {os.getcwd()}")
print(f"📁 __file__: {__file__}")

# Mount static files (for JS, CSS, etc.) - only if directory exists
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/debug")
async def debug_info():
    """Debug endpoint to check frontend path."""
    return {
        "frontend_dir": str(frontend_dir),
        "frontend_exists": frontend_dir.exists(),
        "cwd": os.getcwd(),
        "file": __file__,
        "contents": [str(f) for f in frontend_dir.iterdir()] if frontend_dir.exists() else []
    }


@app.get("/")
async def serve_index():
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        return JSONResponse({"error": "Frontend not found", "path": str(index_file)}, status_code=500)
    return FileResponse(index_file)


@app.get("/{filename}.html")
async def serve_html(filename: str):
    file_path = frontend_dir / f"{filename}.html"
    if file_path.exists():
        return FileResponse(file_path)
    return JSONResponse({"error": "Not found"}, status_code=404)


@app.get("/{filename}.js")
async def serve_js(filename: str):
    file_path = frontend_dir / f"{filename}.js"
    if file_path.exists():
        return FileResponse(file_path, media_type="application/javascript")
    return JSONResponse({"error": "Not found"}, status_code=404)


@app.post("/api/setup")
async def receive_setup(request: Request):
    """Receive interview setup before WebRTC connection."""
    data = await request.json()
    interview_context["current"] = data
    logger.info(f"📋 Received interview setup: {data}")
    return {"status": "ok", "received": data}


@app.get("/api/setup")
async def get_setup():
    """Get current interview setup."""
    return {"setup": interview_context.get("current")}


# Transcript processor to capture AI responses
class TranscriptProcessor(FrameProcessor):
    def __init__(self, connection: SmallWebRTCConnection):
        super().__init__()
        self._connection = connection
        self._current_sentence = ""
    
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, TextFrame) and frame.text:
            self._current_sentence += frame.text
            # Send when we have a complete sentence
            if any(p in frame.text for p in ['.', '!', '?', '\n']):
                if self._current_sentence.strip():
                    try:
                        # Send via data channel using send_app_message (not async)
                        msg = json.dumps({
                            "type": "bot-transcription",
                            "data": self._current_sentence.strip()
                        })
                        self._connection.send_app_message(msg)
                        logger.info(f"📝 Sent transcript: {self._current_sentence.strip()[:50]}...")
                    except Exception as e:
                        logger.warning(f"Could not send transcript: {e}")
                self._current_sentence = ""
        
        await self.push_frame(frame, direction)


async def run_bot(connection: SmallWebRTCConnection, setup_data: dict = None):
    """Run the interview bot for a connection."""
    logger.info(f"Starting bot with setup: {setup_data}")
    
    # Initialize services
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",  # British Lady
    )
    llm = AzureLLMService(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )
    
    # Simli AI Avatar - processes TTS audio and generates video
    simli_ai = SimliVideoService(
        api_key=os.getenv("SIMLI_API_KEY"),
        face_id=os.getenv("SIMLI_FACE_ID"),
    )
    
    # System prompt
    system_prompt = """You are a professional AI interview coach conducting a realistic job interview practice session.

Your role is to:
- Ask relevant behavioral and technical interview questions
- Listen actively to the candidate's responses
- Ask thoughtful follow-up questions when appropriate
- Maintain a professional but friendly demeanor
- Help candidates improve their interview skills through practice
- Keep responses concise and natural, as in a real interview

Interview Guidelines:
1. Tailor questions to the candidate's target role and experience level
2. Ask about past projects, challenges, and achievements
3. Probe for specific examples and details
4. Ask 5-7 questions total, then conclude the interview
5. End by thanking them and wishing them luck

Keep your tone professional yet encouraging. Ask one question at a time and wait for responses."""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add context based on setup
    if setup_data:
        context_msg = f"""The candidate has provided the following information:
- Target Position: {setup_data.get('jobTitle', 'Not specified')}
- Company: {setup_data.get('company', 'Not specified')}
- Interview Format: {setup_data.get('interviewFormat', 'Not specified')}
- Experience: {setup_data.get('experience', 'Not specified')}

Greet the candidate warmly by acknowledging you know they're preparing for the {setup_data.get('jobTitle', 'position')} role at {setup_data.get('company', 'their target company')}. Start with your first interview question directly - do NOT ask them what role they're preparing for since you already know."""
        messages.append({"role": "system", "content": context_msg})
    else:
        messages.append({
            "role": "system", 
            "content": "Greet the candidate warmly and ask what job role they are preparing to interview for. Keep it brief and professional."
        })
    
    context = LLMContext(messages)
    context_aggregator = LLMContextAggregatorPair(context)
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))
    
    # Create transport with video output enabled for Simli avatar
    transport = SmallWebRTCTransport(
        webrtc_connection=connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            video_out_enabled=True,
            video_out_is_live=True,
            video_out_width=512,
            video_out_height=512,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.5)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
    )
    
    # Create transcript processor
    transcript_processor = TranscriptProcessor(connection)
    
    pipeline = Pipeline([
        transport.input(),
        rtvi,
        stt,
        context_aggregator.user(),
        llm,
        transcript_processor,
        tts,
        simli_ai,  # Simli processes TTS audio and outputs video frames
        transport.output(),
        context_aggregator.assistant(),
    ])
    
    task = PipelineTask(
        pipeline,
        params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
        observers=[RTVIObserver(rtvi)],
    )
    
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected - Starting interview")
        await task.queue_frames([LLMRunFrame()])
    
    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()
    
    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)


# Store active connections
connections = {}


@app.post("/api/offer")
async def handle_offer(request: Request):
    """Handle WebRTC SDP offer."""
    try:
        data = await request.json()
        logger.info(f"📥 Received offer: {data.get('type', 'offer')}")
        
        # Capture request_data if provided
        if data.get("request_data"):
            interview_context["current"] = data["request_data"]
            logger.info(f"📋 Captured setup from offer: {data['request_data']}")
        
        # Create WebRTC connection
        connection = SmallWebRTCConnection()
        
        # Get the current setup
        setup_data = interview_context.get("current")
        
        # Initialize with the offer SDP and get answer
        await connection.initialize(data["sdp"], data.get("type", "offer"))
        answer = connection.get_answer()  # Not async - returns dict directly
        
        # Generate connection ID
        pc_id = connection.pc_id or str(id(connection))
        connections[pc_id] = connection
        
        # Start the bot in background
        asyncio.create_task(run_bot(connection, setup_data))
        
        logger.info(f"✅ Offer handled successfully, pc_id: {pc_id}")
        return {
            "sdp": answer["sdp"],
            "type": answer["type"],
            "pc_id": pc_id
        }
    except Exception as e:
        logger.error(f"❌ Error handling offer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/offer")
async def handle_ice_candidate(request: Request):
    """Handle ICE candidates."""
    data = await request.json()
    pc_id = data.get("pc_id")
    candidates = data.get("candidates", [])
    
    connection = connections.get(pc_id)
    if not connection:
        return JSONResponse({"error": "Connection not found"}, status_code=404)
    
    for candidate in candidates:
        await connection.add_ice_candidate(candidate)
    
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    print("\n" + "=" * 60)
    print("🎯 AI Interview Coach Server")
    print("=" * 60)
    print()
    print(f"Open in browser: http://localhost:{port}")
    print()
    print("API Endpoints:")
    print("  POST /api/setup  - Set interview context")
    print("  POST /api/offer  - WebRTC SDP exchange")
    print("  PATCH /api/offer - ICE candidates")
    print("=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

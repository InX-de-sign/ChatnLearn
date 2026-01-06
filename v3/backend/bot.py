"""
Interview Bot V3 - Following Official Pipecat Patterns

Based on Pipecat Quickstart Guide:
- Uses proper runner system
- WebRTC transport with VAD
- Context aggregators
- Event-driven architecture
- Production-ready patterns
"""
import os
import asyncio
from loguru import logger
from dotenv import load_dotenv

# Pipecat Core
from pipecat.frames.frames import LLMMessagesFrame, EndFrame, LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIProcessor, RTVIConfig
from pipecat.observers.rtvi import RTVIObserver
from pipecat.services.azure import AzureLLMService
from pipecat.services.deepgram import DeepgramSTTService, DeepgramTTSService
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.runner.create_transport import create_transport
from pipecat.runner.run import RunnerArguments

# TTS
from gtts import gTTS
import io
import base64

load_dotenv()


class InterviewProcessor(FrameProcessor):
    """
    Custom processor to manage interview flow.
    Tracks questions and determines when to generate summary.
    """
    
    def __init__(self, questions: list, context: OpenAILLMContext):
        super().__init__()
        self.questions = questions
        self.current_index = 0
        self.responses = []
        self.context = context
        logger.info(f"📋 Interview loaded with {len(questions)} questions")
    
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        # Track user responses
        if isinstance(frame, LLMMessagesFrame):
            messages = frame.messages
            # Check for user messages
            for msg in messages:
                if msg.get("role") == "user":
                    self.responses.append(msg.get("content"))
        
        await self.push_frame(frame, direction)
    
    def get_next_question(self):
        """Get next question or None if complete"""
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            self.current_index += 1
            return q
        return None
    
    def is_complete(self):
        """Check if all questions asked"""
        return self.current_index >= len(self.questions)


async def run_bot(transport, runner_args: RunnerArguments):
    """Main bot logic following official Pipecat patterns"""
    
    # Configuration
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-09-01-preview")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    
    logger.info("🚀 Starting Interview Bot V3 (Official Pipecat Patterns)")
    logger.info(f"   Azure: {azure_endpoint}")
    logger.info(f"   Model: {azure_deployment}")
    
    # Interview questions
    questions = [
        "Tell me about yourself and your background.",
        "What interests you most about this role?",
        "Describe a challenging project you've worked on recently.",
        "How do you handle tight deadlines and pressure?",
        "Where do you see yourself in five years?"
    ]
    
    # =======================
    # AI Services (Official)
    # =======================
    
    # Speech-to-Text
    stt = DeepgramSTTService(api_key=deepgram_api_key)
    
    # Text-to-Speech (using gTTS for natural voice)
    # Note: We'll use gTTS instead of Cartesia/Deepgram TTS
    
    # Language Model
    llm = AzureLLMService(
        api_key=azure_api_key,
        endpoint=azure_endpoint,
        model=azure_deployment,
        api_version=azure_api_version,
    )
    
    # =======================
    # Context & Messages (Official Pattern)
    # =======================
    
    # System prompt
    system_msg = """You are a professional job interviewer conducting a behavioral interview.

Guidelines:
- Acknowledge candidate responses briefly (1-2 sentences)
- Transition naturally to the next question
- Stay professional and formal
- Keep responses concise
- You'll receive questions to ask - incorporate them naturally"""
    
    messages = [
        {"role": "system", "content": system_msg}
    ]
    
    # Create context
    context = OpenAILLMContext(messages=messages)
    context_aggregator = llm.create_context_aggregator(context)
    
    # Interview processor
    interview_processor = InterviewProcessor(questions, context)
    
    # =======================
    # RTVI Protocol (Official)
    # =======================
    
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))
    
    # =======================
    # Pipeline (Official Pattern)
    # =======================
    
    pipeline = Pipeline([
        transport.input(),              # Audio from browser
        rtvi,                           # RTVI protocol
        stt,                            # Speech-to-text
        context_aggregator.user(),      # Add user message to context
        interview_processor,            # Track interview state
        llm,                            # Generate response
        # Note: TTS will be handled separately for gTTS
        transport.output(),             # Audio to browser
        context_aggregator.assistant(), # Add bot response to context
    ])
    
    # =======================
    # Pipeline Task (Official)
    # =======================
    
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )
    
    # =======================
    # Event Handlers (Official Pattern)
    # =======================
    
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("👤 Client connected")
        
        # Send greeting with first question
        first_q = interview_processor.get_next_question()
        greeting = f"Hello! Welcome to your interview. You'll have 30 seconds to answer each question. Let's begin. {first_q}"
        
        # Add greeting to context
        messages.append({"role": "assistant", "content": greeting})
        
        # Prompt the bot to start talking
        await task.queue_frames([LLMRunFrame()])
    
    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("👤 Client disconnected")
        await task.cancel()
    
    # =======================
    # Run Pipeline (Official)
    # =======================
    
    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """
    Main bot entry point (Official Pattern).
    
    This follows the official Pipecat runner system.
    """
    
    # Transport parameters for WebRTC
    transport_params = {
        "daily": lambda: DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            vad_enabled=True,
        ),
    }
    
    # Create transport
    transport = await create_transport(runner_args, transport_params)
    
    # Run the bot
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    # Use official Pipecat runner
    from pipecat.runner.run import main
    main()

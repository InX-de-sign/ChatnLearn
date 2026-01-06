"""
FastAPI server for real-time AI interview chatbot using Pipecat
"""
import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Interview AI API")

# Configure CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active sessions
active_sessions = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Interview AI API is running"}


@app.websocket("/ws/interview")
async def websocket_interview(websocket: WebSocket):
    """
    WebSocket endpoint for real-time interview session (original version)
    """
    await websocket.accept()
    logger.info("Client connected to interview session")
    
    try:
        # Import and run bot
        from bot_simple import run_bot_websocket
        await run_bot_websocket(websocket)
        
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error in interview session: {str(e)}")
        try:
            await websocket.close()
        except:
            pass


@app.websocket("/ws/interview-realtime")
async def websocket_interview_realtime(websocket: WebSocket):
    """
    WebSocket endpoint for real-time interview simulation (new version)
    No chat interface, just conversation with final feedback
    """
    await websocket.accept()
    logger.info("Client connected to real-time interview session")
    
    try:
        # Import and run interview bot
        from bot_interview import run_interview_bot
        await run_interview_bot(websocket)
        
    except WebSocketDisconnect:
        logger.info("Client disconnected from real-time interview")
    except Exception as e:
        logger.error(f"Error in real-time interview session: {str(e)}")
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

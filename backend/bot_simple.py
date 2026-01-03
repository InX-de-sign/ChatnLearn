"""
Azure OpenAI bot using WebSocket transport
"""
import os
import asyncio
import json
import aiohttp
from fastapi import WebSocket
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def run_bot_websocket(websocket: WebSocket):
    """
    Run the bot with Azure OpenAI via WebSocket
    
    Args:
        websocket: FastAPI WebSocket connection
    """
    
    logger.info("Starting bot session")
    
    # Azure OpenAI settings (REQUIRED)
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Validate Azure configuration
    if not azure_api_key or not azure_endpoint or not azure_deployment:
        logger.error("❌ Missing Azure OpenAI configuration in .env file")
        await websocket.send_json({
            "type": "error",
            "content": "Server configuration error: Missing Azure OpenAI settings"
        })
        return
    
    logger.info(f"✅ Using Azure OpenAI at: {azure_endpoint}")
    logger.info(f"   Deployment: {azure_deployment}")
    logger.info(f"   API Version: {azure_api_version}")
    
    # System prompt for interview assistant
    system_prompt = """You are an AI interview coach helping users practice for job interviews.

Your role is to:
1. Ask relevant interview questions based on the job role the user mentions
2. Provide constructive feedback on their answers
3. Help them improve their communication skills
4. Be encouraging and supportive while being honest about areas for improvement
5. Ask follow-up questions to help them think deeper

Start by asking what role they're interviewing for, then conduct a realistic interview practice session.
Keep your responses concise and natural, as if you're in a real interview."""
    
    # Initialize conversation history
    conversation_history = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Send initial greeting
    initial_message = "Hello! I'm your AI interview coach. What role are you preparing to interview for?"
    conversation_history.append({"role": "assistant", "content": initial_message})
    
    await websocket.send_json({
        "type": "message",
        "role": "assistant",
        "content": initial_message
    })
    
    try:
        # Main conversation loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                user_message = data.get("content", "")
                logger.info(f"User: {user_message}")
                
                # Add user message to history
                conversation_history.append({
                    "role": "user",
                    "content": user_message
                })
                
                # Generate AI response using Azure OpenAI
                try:
                    # Check if using Azure API Management (azure-api.net) or direct Azure OpenAI
                    is_api_management = "azure-api.net" in azure_endpoint
                    
                    if is_api_management:
                        # Azure API Management endpoint
                        url = f"{azure_endpoint.rstrip('/')}/openai/deployments/{azure_deployment}/chat/completions?api-version={azure_api_version}"
                    else:
                        # Direct Azure OpenAI endpoint
                        url = f"{azure_endpoint.rstrip('/')}/openai/deployments/{azure_deployment}/chat/completions?api-version={azure_api_version}"
                    
                    headers = {
                        "Content-Type": "application/json",
                        "api-key": azure_api_key
                    }
                    
                    payload = {
                        "messages": conversation_history,
                        "max_tokens": 300,
                        "temperature": 0.7
                    }
                    
                    logger.info(f"📤 Calling Azure: {url}")
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, json=payload, headers=headers) as resp:
                            if resp.status != 200:
                                error_text = await resp.text()
                                logger.error(f"❌ Azure API error ({resp.status}): {error_text}")
                                
                                await websocket.send_json({
                                    "type": "error",
                                    "content": f"Azure API error: {resp.status}"
                                })
                                continue
                            
                            result = await resp.json()
                            assistant_message = result['choices'][0]['message']['content']
                            logger.info(f"🤖 Assistant: {assistant_message}")
                    
                    # Add to history
                    conversation_history.append({
                        "role": "assistant",
                        "content": assistant_message
                    })
                    
                    # Send response to client
                    await websocket.send_json({
                        "type": "message",
                        "role": "assistant",
                        "content": assistant_message
                    })
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error generating response: {e}")
                    
                    # Send helpful error message to user
                    if "unsupported_country" in error_msg or "403" in error_msg:
                        await websocket.send_json({
                            "type": "error",
                            "content": "⚠️ OpenAI blocked your region. Please use a VPN (US/EU server) or check your API key."
                        })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "content": f"Sorry, I encountered an error: {error_msg[:100]}"
                        })
            
            elif data.get("type") == "end":
                logger.info("Session ended by client")
                break
                
    except Exception as e:
        logger.error(f"Error in bot session: {e}")
    finally:
        logger.info("Bot session ended")

# 🎯 AI Interview Coach

A real-time conversational AI chatbot built with [Pipecat](https://github.com/pipecat-ai/pipecat) for interview preparation. Practice your interview skills with an AI coach that provides real-time feedback through text chat.

## ✅ Currently Working

The project is **fully functional** with text-based chat! The typo in your installation command (`pip install requirememtns` instead of `pip install -r requirements.txt`) has been fixed and all dependencies are now installed.

## Features

- 💬 **Real-time Chat**: Natural conversation with AI interview coach
- 🤖 **Smart AI**: Powered by GPT-4 Mini for fast, realistic interviews
- 📱 **Web-based**: No installation, works in your browser
- 🎯 **Interview Focused**: Tailored for job interview preparation
- 🚀 **Fast & Simple**: WebSocket-based for instant responses

## Prerequisites

- Python 3.10+ (you have 3.13.5 ✓)
- [OpenAI API Key](https://platform.openai.com/api-keys) **(Required)**

## Quick Start

### 1. Add your API key

Edit `backend/.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. Start the server

The server is ALREADY RUNNING on `http://localhost:8000` ✓

If you need to restart it:
```bash
cd backend
python server.py
```

### 3. Open the chat interface

Open `frontend/chat.html` in your browser:
- Double-click the file, or
- Visit `file:///f:/_CNL/frontend/chat.html`

### 4. Start practicing!

Click "Start Interview Practice" and begin your mock interview!

## Troubleshooting

### ❌ "ModuleNotFoundError"
**Fixed!** You typed `pip install requirememtns` instead of `pip install -r requirements.txt`. 
All packages are now installed correctly.

### Missing API key error
Edit `backend/.env` and replace `your_openai_api_key_here` with your actual OpenAI API key.

### WebSocket connection fails
Make sure the backend server is running on port 8000.

## Project Structure

```
_CNL/
├── backend/
│   ├── server.py         # FastAPI server ✓ Running
│   ├── bot_simple.py     # AI bot logic
│   ├── .env              # Add your API key here!
│   └── requirements.txt  # All installed ✓
└── frontend/
    └── chat.html         # Open this in browser!
```

## How It Works

1. User opens `chat.html` in browser
2. Clicks "Start Interview Practice"
3. WebSocket connects to backend server
4. AI coach greets and starts interview
5. User types answers, AI responds with follow-ups
6. Natural back-and-forth conversation

## Customization

### Change AI personality
Edit `backend/bot_simple.py` line 30

### Use different model
Edit `backend/bot_simple.py` line 50:
- `gpt-4o-mini` (current - fast & cheap)
- `gpt-4o` (smarter but slower)
- `gpt-3.5-turbo` (fastest & cheapest)

## What's Next?

Current version uses **text chat only**. To add voice/video:
- Get [Deepgram API key](https://console.deepgram.com/)
- Get [Daily.co API key](https://dashboard.daily.co/) 
- Wait for `daily-python` Python 3.13 support
- Switch to `bot.py` and `index.html`

## License

MIT License

## Built With

- [Pipecat](https://github.com/pipecat-ai/pipecat) - Voice AI framework
- [OpenAI](https://openai.com/) - GPT models
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

# 🎯 AI Interview Coach v1

A real-time conversational AI chatbot for interview preparation with two interview modes: interactive chat practice and full interview simulation.

## ✅ Currently Working

The project is **fully functional** and deployed! Both chat and real-time interview modes are working.

- **Live Demo**: [https://chatnlearnfiona.vercel.app/](https://chatnlearnfiona.vercel.app/)
- **Backend API**: [https://chatnlearn-production.up.railway.app/](https://chatnlearn-production.up.railway.app/)

## Features

- 💬 **Interactive Chat Mode**: Practice with real-time feedback and follow-up questions
- 🎬 **Real-Time Interview Mode**: Complete interview simulation with final feedback only
- 🤖 **Azure OpenAI GPT-4**: Powered by Azure OpenAI for intelligent, context-aware responses
- 📱 **Web-based**: No installation required, works directly in browser
- 🎯 **Interview Focused**: Tailored questions based on job role, company, and experience level
- 🚀 **Fast & Reliable**: WebSocket-based for instant responses
- 🔄 **Auto Environment Detection**: Automatically switches between local and production URLs

## Prerequisites

- Python 3.10+
- [Azure OpenAI API Access](https://azure.microsoft.com/en-us/products/ai-services/openai-service) **(Required)**

## Quick Start

### 1. Configure Azure OpenAI

Create a `.env` file in the `backend/` directory with your Azure OpenAI credentials:

```bash
cd backend
```

Create `.env` file:
```
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt4-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python server.py
```

The server will start on `http://localhost:8000`

### 4. Open the Interface

Open `frontend/index.html` in your browser to access both interview modes.

## Interview Modes

### Chat Mode (`chat_mode.html`)
- Interactive practice with real-time AI feedback
- Ask follow-up questions and provide guidance
- WebSocket endpoint: `/ws/interview`
- Uses `bot_simple.py` for conversational AI

### Real-Time Interview (`video_mode.html`)
- Complete interview simulation without intermediate feedback
- Structured question flow with final assessment
- WebSocket endpoint: `/ws/interview-realtime`
- Uses `bot_interview.py` for full interview experience

## Project Structure

```
v1/
├── backend/
│   ├── server.py           # FastAPI server with 2 WebSocket endpoints
│   ├── bot_simple.py       # Interactive chat bot logic
│   ├── bot_interview.py    # Real-time interview simulation bot
│   ├── requirements.txt    # Python dependencies
│   ├── pyproject.toml      # Project configuration
│   └── .env               # Azure OpenAI credentials (create this)
├── frontend/
│   ├── index.html         # Landing page with mode selection
│   ├── chat_mode.html     # Interactive chat interface
│   ├── video_mode.html    # Real-time interview interface
│   ├── info_gather.html   # Interview setup form
│   ├── config.js          # Environment detection & API URLs
│   └── vercel.json        # Vercel deployment config
└── README.md             # This file
```

## How It Works

### Backend Architecture
- **FastAPI Server**: Handles HTTP health checks and WebSocket connections
- **Two WebSocket Endpoints**:
  - `/ws/interview`: Interactive chat with `bot_simple.py`
  - `/ws/interview-realtime`: Full interview with `bot_interview.py`
- **Azure OpenAI Integration**: Direct API calls for GPT-4 responses
- **Environment Detection**: Frontend automatically detects local vs production

### Frontend Flow
1. User visits `index.html` and selects interview mode
2. `info_gather.html` collects interview context (job, company, experience)
3. Chat mode: Real-time conversation with AI feedback
4. Real-time mode: Structured interview with final evaluation

## Configuration

### Environment Variables
```bash
# Required Azure OpenAI settings
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4  # or your custom deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional: Server port (defaults to 8000)
PORT=8000
```

### Frontend Configuration
The `config.js` file automatically detects the environment:
- **Local**: `ws://localhost:8000` and `http://localhost:8000`
- **Production**: Uses Railway URLs for backend communication

## Troubleshooting

### ❌ "Missing Azure OpenAI configuration"
- Ensure `.env` file exists in `backend/` directory
- Verify all four Azure OpenAI variables are set correctly
- Check your Azure OpenAI resource is active and accessible

### WebSocket Connection Issues
- **Local**: Ensure backend server is running on port 8000
- **Production**: Check Railway deployment status
- **CORS**: Backend allows all origins for development

### Module Import Errors
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Customization

### Modify Interview Questions
Edit `backend/bot_interview.py` to customize the question pool based on job types and focus areas.

### Change AI Personality
Update the system prompts in `backend/bot_simple.py` and `backend/bot_interview.py`.

### Add New Interview Modes
1. Create new bot file in `backend/`
2. Add new WebSocket endpoint in `server.py`
3. Create corresponding HTML interface in `frontend/`

## Deployment

### Backend (Railway)
The backend is configured for Railway deployment with `railway.json` and environment variables set in Railway dashboard.

### Frontend (Vercel)
Frontend files are ready for Vercel deployment. The `vercel.json` configures proper routing.

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - GPT-4 AI models
- [WebSockets](https://websockets.readthedocs.io/) - Real-time communication
- [Railway](https://railway.app/) - Backend deployment
- [Vercel](https://vercel.com/) - Frontend deployment

## License

MIT License

## Troubleshooting

### ❌ "ModuleNotFoundError"
**Fixed!** You typed `pip install requirememtns` instead of `pip install -r requirements.txt`. 
All packages are now installed correctly.

### Missing API key error
Edit `backend/.env` and replace `your_openai_api_key_here` with your actual OpenAI API key.

### WebSocket Connection Issues
- **Local**: Ensure backend server is running on port 8000
- **Production**: Check Railway deployment status
- **CORS**: Backend allows all origins for development

### Module Import Errors
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Project Structure

```
v1/
├── backend/
│   ├── server.py           # FastAPI server with 2 WebSocket endpoints
│   ├── bot_simple.py       # Interactive chat bot logic
│   ├── bot_interview.py    # Real-time interview simulation bot
│   ├── requirements.txt    # Python dependencies
│   ├── pyproject.toml      # Project configuration
│   └── .env               # Azure OpenAI credentials (create this)
├── frontend/
│   ├── index.html         # Landing page with mode selection
│   ├── chat_mode.html     # Interactive chat interface
│   ├── video_mode.html    # Real-time interview interface
│   ├── info_gather.html   # Interview setup form
│   ├── config.js          # Environment detection & API URLs
│   └── vercel.json        # Vercel deployment config
└── README.md             # This file
```

## How It Works

### Backend Architecture
- **FastAPI Server**: Handles HTTP health checks and WebSocket connections
- **Two WebSocket Endpoints**:
  - `/ws/interview`: Interactive chat with `bot_simple.py`
  - `/ws/interview-realtime`: Full interview with `bot_interview.py`
- **Azure OpenAI Integration**: Direct API calls for GPT-4 responses
- **Environment Detection**: Frontend automatically detects local vs production

### Frontend Flow
1. User visits `index.html` and selects interview mode
2. `info_gather.html` collects interview context (job, company, experience)
3. Chat mode: Real-time conversation with AI feedback
4. Real-time mode: Structured interview with final evaluation

## Customization

### Modify Interview Questions
Edit `backend/bot_interview.py` to customize the question pool based on job types and focus areas.

### Change AI Personality
Update the system prompts in `backend/bot_simple.py` and `backend/bot_interview.py`.

### Add New Interview Modes
1. Create new bot file in `backend/`
2. Add new WebSocket endpoint in `server.py`
3. Create corresponding HTML interface in `frontend/`

## Deployment

### Backend (Railway)
The backend is configured for Railway deployment with `railway.json` and environment variables set in Railway dashboard.

### Frontend (Vercel)
Frontend files are ready for Vercel deployment. The `vercel.json` configures proper routing.

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - GPT-4 AI models
- [WebSockets](https://websockets.readthedocs.io/) - Real-time communication
- [Railway](https://railway.app/) - Backend deployment
- [Vercel](https://vercel.com/) - Frontend deployment

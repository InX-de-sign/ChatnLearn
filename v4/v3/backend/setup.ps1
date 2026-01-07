# V3 Setup Script - Following Official Pipecat Patterns

Write-Host "🚀 Setting up Interview Bot V3 (Official Pipecat)" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

if ($pythonVersion -notmatch "Python 3\.(10|11|12|13)") {
    Write-Host "⚠️  Warning: Python 3.10+ recommended" -ForegroundColor Yellow
}

Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host ""
Write-Host "Installing Pipecat and dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes (Pipecat has many components)..." -ForegroundColor Gray
pip install -r requirements.txt

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "⚠️  .env file not found!" -ForegroundColor Red
    Write-Host "Copying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "📝 Please edit .env file with your API keys:" -ForegroundColor Cyan
    Write-Host "   - AZURE_OPENAI_API_KEY" -ForegroundColor White
    Write-Host "   - AZURE_OPENAI_ENDPOINT" -ForegroundColor White
    Write-Host "   - DEEPGRAM_API_KEY" -ForegroundColor White
    Write-Host "   - DAILY_API_KEY" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✅ .env file found" -ForegroundColor Green
}

Write-Host ""
Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 V3 uses OFFICIAL Pipecat patterns:" -ForegroundColor Cyan
Write-Host "   - Runner system (main())" -ForegroundColor White
Write-Host "   - Daily WebRTC transport" -ForegroundColor White
Write-Host "   - Full pipeline automation" -ForegroundColor White
Write-Host "   - Context aggregators" -ForegroundColor White
Write-Host "   - RTVI protocol" -ForegroundColor White
Write-Host ""
Write-Host "To start the bot:" -ForegroundColor Cyan
Write-Host "  python bot.py" -ForegroundColor White
Write-Host ""
Write-Host "Then open: http://localhost:7860/client" -ForegroundColor Yellow
Write-Host ""

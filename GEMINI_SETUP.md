# Updated to use Google Gemini instead of OpenAI

## Quick Start

1. Get your Google API key: https://aistudio.google.com/apikey
2. Set it in your environment:
   ```bash
   export GOOGLE_API_KEY=your-key-here
   ```
3. Run the server:
   ```bash
   uv run uvicorn src.main:app --reload
   ```

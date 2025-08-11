# OpenAI API Setup

To use the AI-powered parsing feature, you'll need an OpenAI API key.

## Getting an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to "API Keys" in your dashboard
4. Click "Create new secret key"
5. Copy the generated API key

## Using the API Key

### Option 1: Web Interface (Recommended)
- Simply enter your API key when selecting "AI-Powered Parsing"
- The key is used only for that session and is not stored

### Option 2: Environment Variable
Create a `.env` file in your project root:
```
OPENAI_API_KEY=your_actual_api_key_here
```

### Option 3: Direct Initialization
```python
from ai_agent import LinkedInDataExtractor

# Initialize with API key
agent = LinkedInDataExtractor(openai_api_key="your_api_key_here")
```

## Cost Information
- GPT-4 API calls cost approximately $0.03 per 1K input tokens
- Typical LinkedIn MHTML files use 2-5K tokens
- Cost per file: approximately $0.06 - $0.15

## Security Notes
- Never commit your API key to version control
- The web interface does not store your API key
- Consider using environment variables for production deployments 
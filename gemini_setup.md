# Gemini Setup Guide

This guide will help you set up Google Gemini integration for the LinkedIn Data Extraction AI Agent.

## 🚀 Quick Start

### 1. Get Your Google API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API key" or navigate to the API keys section
4. Create a new API key
5. Copy the API key (it will look like: `AIzaSyC...`)

### 2. Set Environment Variable (Recommended)

Add your API key to your environment:

```bash
# macOS/Linux
export GOOGLE_API_KEY="your_api_key_here"

# Windows (Command Prompt)
set GOOGLE_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:GOOGLE_API_KEY="your_api_key_here"
```

### 3. Test the Integration

Run the test script to verify everything works:

```bash
python3 test_ai_models.py
```

## 🔧 Advanced Setup

### Using .env File

Create a `.env` file in your project root:

```bash
# .env
GOOGLE_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional
```

### Direct Usage in Code

```python
from ai_agent import LinkedInDataExtractor

# Initialize with Gemini
agent = LinkedInDataExtractor(
    gemini_api_key="your_api_key_here",
    ai_model="gemini"
)

# Process a file with AI enhancement
results = agent.process_mhtml_file("your_file.mhtml", use_ai=True, ai_model="gemini")
```

## 🔄 How It Works

### Two-Stage Processing

1. **Stage 1: Traditional Parsing**
   - Always runs first for reliable data extraction
   - Extracts: Name, Title, Period, Details
   - Fast and consistent results

2. **Stage 2: AI Enhancement (Optional)**
   - Enhances traditional parsing results
   - Adds: Company name, Location/Remote status
   - Uses Gemini 2.0 Flash Lite for cost-effective enhancement

### Enhanced Data Structure

The final output includes all these fields:
- **Name**: LinkedIn user's name
- **Title**: Professional title/description  
- **Period**: Time period or date information
- **Details**: Post content or additional information
- **Company**: Company name (AI-enhanced)
- **Location**: Remote status or specific location (AI-enhanced)

## 💰 Cost Information

- **Gemini 2.0 Flash Lite**: Very cost-effective
- **Input Tokens**: ~1-3K tokens per enhancement (much less than full parsing)
- **Cost per File**: Approximately $0.005 - $0.02
- **Free Tier**: Generous free tier available

## 🆚 ChatGPT vs Gemini

| Feature | ChatGPT | Gemini |
|---------|---------|---------|
| **Model** | GPT-4 | Gemini 2.0 Flash Lite |
| **Cost** | $0.02-0.08/file | $0.005-0.02/file |
| **Quality** | Excellent | Very Good |
| **Speed** | Fast | Very Fast |
| **Availability** | High | High |

## 🚨 Troubleshooting

### Common Issues

1. **"Gemini client not initialized"**
   - Check if your API key is correct
   - Verify the API key has proper permissions
   - Ensure you have sufficient credits

2. **"Failed to parse Gemini response as JSON"**
   - This is usually a temporary issue
   - The system will fall back to traditional parsing results
   - Try processing the file again

3. **API Rate Limits**
   - Gemini has generous rate limits
   - If you hit limits, wait a few minutes and retry

### Getting Help

- Check the [Google AI Studio documentation](https://ai.google.dev/)
- Verify your API key permissions
- Test with a simple MHTML file first

## 🔒 Security Notes

- API keys are never stored or logged
- All processing is done through Google's secure API
- Use environment variables for production deployments
- Never commit API keys to version control

---

**Ready to use Gemini?** Start by getting your API key from [Google AI Studio](https://aistudio.google.com/)!

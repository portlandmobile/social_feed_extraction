# LinkedIn Data Extraction AI Agent

An intelligent, web-based AI agent that automatically extracts names, titles, periods, and details from LinkedIn MHTML files with advanced parsing capabilities and data quality analysis.

## 🚀 Features

### Core Capabilities
- **Two-Stage Processing**: Traditional parsing followed by optional AI enhancement
- **Enhanced Data Extraction**: Names, titles, periods, details, company names, and location/remote status
- **AI-Powered Enhancement**: Optional GPT-4 or Gemini 2.0 Flash Lite integration for deeper insights
- **Multiple Export Formats**: CSV, JSON, and online viewing options
- **Modern Web Interface**: Drag & drop file upload with real-time processing
- **Secure Processing**: Local file processing with automatic cleanup

### AI Agent Intelligence
- **Two-Stage Processing**: Always starts with traditional parsing for reliability, then optionally enhances with AI
- **AI Enhancement**: Adds company names and location/remote status to traditional parsing results
- **Quality Assessment**: Calculates data extraction quality scores
- **Pattern Recognition**: Identifies common keywords and trends in extracted data
- **Smart Recommendations**: Provides actionable insights for improving extraction results

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup
1. **Clone or download** the project files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Directory Structure
```
ai_news_chart/
├── ai_agent.py              # Core AI agent logic
├── web_interface.py         # Flask web application
├── templates/               # HTML templates
│   ├── index.html          # Main upload page
│   └── results.html        # Results display page
├── requirements.txt         # Python dependencies
├── start_ai_agent.py       # Startup script
└── uploads/                 # Temporary file storage (auto-created)
```

## 🚀 Quick Start

### Option 1: Simple Startup Script
```bash
python start_ai_agent.py
```

### Option 2: Direct Flask Run
```bash
python web_interface.py
```

### Option 3: Command Line Usage
```bash
python ai_agent.py
```

## 🌐 Web Interface Usage

1. **Open your browser** and go to `http://localhost:5000`
2. **Upload MHTML file** by dragging & dropping or clicking to browse
3. **Wait for AI processing** - the agent will analyze and extract data
4. **Review results** with quality scores and insights
5. **Export data** in CSV or JSON format

## 🔧 Advanced Usage

### Command Line Interface
```python
from ai_agent import LinkedInDataExtractor

# Initialize the AI agent
agent = LinkedInDataExtractor()

# Process an MHTML file
results = agent.process_mhtml_file('/path/to/your/file.mhtml')

# Check results
if results.get("success"):
    print(f"Extracted {len(results['extracted_data'])} posts")
    print(f"Quality score: {results['analysis']['data_quality_score']}%")
    
    # Export to different formats
    csv_file = agent.export_to_csv(results['extracted_data'])
    json_file = agent.export_to_json(results['extracted_data'])
```

### API Endpoints
- `GET /` - Main upload page
- `POST /upload` - File upload and processing
- `POST /api/process` - API endpoint for programmatic access
- `GET /export/csv` - Export data as CSV
- `GET /export/json` - Export data as JSON
- `GET /health` - Health check endpoint

## 🧠 AI Agent Intelligence

### Multiple Parsing Strategies
The AI agent uses several fallback strategies to ensure robust data extraction:

1. **Primary Selectors**: Standard LinkedIn HTML classes
2. **Fallback Selectors**: Alternative CSS selectors for different formats
3. **Pattern Matching**: Regular expressions for text extraction
4. **Content Validation**: Quality checks on extracted data

### Data Quality Analysis
- **Completeness Score**: Percentage of successfully extracted fields
- **Pattern Recognition**: Common keywords and trends identification
- **Format Detection**: Automatic LinkedIn version detection
- **Recommendations**: Actionable insights for improvement

### Adaptive Learning
- **Selector Optimization**: Tries multiple approaches for each data field
- **Error Handling**: Graceful degradation when primary methods fail
- **Format Flexibility**: Handles various LinkedIn HTML structures

## 📊 Data Output

### Extracted Fields
- **Name**: LinkedIn user's name
- **Title**: Professional title/description
- **Period**: Time period or date information
- **Details**: Post content or additional information
- **Company**: Company name (AI-enhanced)
- **Location**: Remote status or specific location (AI-enhanced)
- **Post_Index**: Sequential post number

### Export Formats
- **CSV**: Standard spreadsheet format
- **JSON**: Structured data format
- **Online View**: Interactive web table with expandable rows

## 🔒 Security Features

- **Local Processing**: All files processed locally, no external uploads
- **Automatic Cleanup**: Temporary files deleted after processing
- **File Validation**: Type and size restrictions
- **Secure Filenames**: Sanitized file names to prevent path traversal

## 🤖 AI Integration

### AI-Powered Parsing
The AI agent now supports both OpenAI ChatGPT and Google Gemini for enhanced parsing capabilities:

#### Available AI Models
- **ChatGPT (OpenAI)**: Uses GPT-4 for optimal extraction quality
- **Gemini (Google)**: Uses Gemini 2.0 Flash Lite for cost-effective extraction

#### When to Use AI Parsing
- **Complex Formats**: Non-standard LinkedIn HTML structures
- **Fallback Option**: When traditional parsing fails or produces low-quality results
- **Advanced Extraction**: Need for more nuanced data interpretation

#### Setup Requirements

##### ChatGPT (OpenAI)
1. **OpenAI API Key**: Get your key from [OpenAI Platform](https://platform.openai.com/)
2. **API Credits**: Ensure you have sufficient credits (costs ~$0.06-0.15 per file)
3. **Internet Connection**: Required for API calls

##### Gemini (Google)
1. **Google API Key**: Get your key from [Google AI Studio](https://aistudio.google.com/)
2. **API Credits**: Ensure you have sufficient credits (costs ~$0.01-0.05 per file)
3. **Internet Connection**: Required for API calls

#### Usage Options
1. **Web Interface**: Select "AI-Powered Parsing" and choose your preferred model
2. **Environment Variables**: Set `OPENAI_API_KEY` and/or `GOOGLE_API_KEY` in your `.env` file
3. **Direct Initialization**: Pass API keys to `LinkedInDataExtractor(openai_api_key="...", gemini_api_key="...", ai_model="...")`

#### Cost Information
- **ChatGPT**: ~2-5K tokens per typical LinkedIn MHTML file (~$0.06 - $0.15 per file)
- **Gemini**: ~2-5K tokens per typical LinkedIn MHTML file (~$0.01 - $0.05 per file)
- **Model Selection**: Choose based on your budget and quality requirements

#### Security Notes
- API keys are never stored or logged
- All processing is done through secure APIs
- Consider using environment variables for production deployments

For detailed setup instructions, see `openai_setup.md`.

## 🚨 Troubleshooting

### Common Issues

1. **"No data extracted"**
   - Check if the MHTML file contains LinkedIn content
   - Verify the file format (.mhtml or .mht)
   - Try a different LinkedIn export

2. **Low quality scores**
   - The AI agent will provide specific recommendations
   - Check if LinkedIn's HTML structure has changed
   - Verify the file isn't corrupted

3. **Template errors**
   - Ensure you're running from the project root directory
   - Check that the `templates/` folder exists
   - Verify all dependencies are installed

### Performance Tips
- **File Size**: Keep MHTML files under 50MB for optimal performance
- **Browser**: Use modern browsers for the best web interface experience
- **Processing**: Large files may take several seconds to process

## 🔮 Future Enhancements

### Planned Features
- **Batch Processing**: Handle multiple files simultaneously
- **Advanced Analytics**: Machine learning for better pattern recognition
- **API Integration**: Connect with external data sources
- **Custom Export Formats**: User-defined output formats
- **Real-time Processing**: Stream processing for large files

### Extensibility
The AI agent is designed to be easily extensible:
- **New Parsers**: Add support for different LinkedIn formats
- **Custom Fields**: Extract additional data types
- **Integration**: Connect with other business intelligence tools

## 📝 License

This project is provided as-is for educational and business use. Please ensure compliance with LinkedIn's terms of service when extracting data.

## 🤝 Contributing

To contribute to the AI agent:
1. **Fork the repository**
2. **Create a feature branch**
3. **Implement improvements**
4. **Test thoroughly**
5. **Submit a pull request**

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Test with a simple MHTML file first
4. Ensure all dependencies are properly installed

---

**Built with ❤️ using Python, Flask, and BeautifulSoup** 
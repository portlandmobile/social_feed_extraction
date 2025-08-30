# Production Deployment Guide

## Setting Up Environment Variables for API Keys

### For Google Cloud Run:

#### Method 1: Cloud Console (Recommended)
1. Go to your Cloud Run service in Google Cloud Console
2. Click "EDIT & DEPLOY NEW REVISION"
3. In the "Variables & Secrets" section, add:
   - `OPENAI_API_KEY` = `your_actual_openai_key`
   - `GEMINI_API_KEY` = `your_actual_gemini_key`
4. Deploy the new revision

#### Method 2: gcloud CLI
```bash
gcloud run services update YOUR_SERVICE_NAME \
  --set-env-vars OPENAI_API_KEY=your_openai_key,GEMINI_API_KEY=your_gemini_key \
  --region=YOUR_REGION
```

#### Method 3: YAML Configuration
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: your-service-name
spec:
  template:
    spec:
      containers:
      - image: your-image
        env:
        - name: OPENAI_API_KEY
          value: "your_openai_key"
        - name: GEMINI_API_KEY
          value: "your_gemini_key"
```

### For Local Development:
1. Create a `.env` file in your project root
2. Add your API keys:
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   GEMINI_API_KEY=your_gemini_key_here
   ```
3. Never commit the `.env` file to version control

### Security Notes:
- ✅ API keys are encrypted at rest in Google Cloud
- ✅ Keys are never visible in your code repository
- ✅ Keys can be rotated without code changes
- ✅ Access is controlled via IAM permissions
- ✅ Keys are isolated per service

### Environment Variable Names:
- `OPENAI_API_KEY` - Your OpenAI API key for ChatGPT enhancement
- `GEMINI_API_KEY` - Your Google API key for Gemini enhancement

### Testing:
After setting environment variables, restart your service and test with:
1. Upload an MHTML file
2. Select "AI Enhancement" 
3. Choose your preferred AI model
4. The system will automatically use the environment variables

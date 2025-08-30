# Deployment Scripts for LinkedIn Data Extractor

This directory contains deployment scripts to deploy your LinkedIn Data Extractor application to Google Cloud Run with Firestore.

## 🚀 Available Scripts

### 1. `deploy_to_cloud_run.sh` - Interactive Deployment
**Full-featured deployment script with user prompts and validation.**

**Features:**
- ✅ Interactive prompts for all configuration
- ✅ Automatic validation of Google Cloud project
- ✅ Checks and enables Firestore API
- ✅ Configures environment variables
- ✅ Comprehensive error handling
- ✅ Colored output for better readability

**Usage:**
```bash
./deploy_to_cloud_run.sh
```

**What it does:**
1. Checks prerequisites (gcloud, Docker)
2. Validates Google Cloud authentication
3. Prompts for project ID, service name, region
4. Collects API keys (optional)
5. Sets environment variables
6. Deploys to Cloud Run
7. Provides deployment summary and next steps

### 2. `deploy_quick.sh` - Quick Deployment
**Fast deployment script for when you know all parameters.**

**Features:**
- ✅ Command-line arguments for quick deployment
- ✅ Minimal prompts
- ✅ Fast execution
- ✅ Perfect for CI/CD or repeated deployments

**Usage:**
```bash
# Basic usage (uses defaults for service name and region)
./deploy_quick.sh YOUR_PROJECT_ID

# Custom service name and region
./deploy_quick.sh YOUR_PROJECT_ID linkedin-extractor us-central1
```

**What it does:**
1. Sets Google Cloud project
2. Enables Firestore API
3. Deploys to Cloud Run with Firestore configuration
4. Provides service URL and next steps

## 📋 Prerequisites

Before using these scripts, ensure you have:

1. **Google Cloud SDK** installed and configured
   ```bash
   # Install gcloud CLI
   # Visit: https://cloud.google.com/sdk/docs/install
   
   # Authenticate
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Docker** installed and running
   ```bash
   # Install Docker Desktop or Docker Engine
   # Visit: https://docs.docker.com/get-docker/
   ```

3. **Firestore Database** created in your Google Cloud project
   - Go to Google Cloud Console → Firestore
   - Click "Create Database"
   - Choose "Native mode" and select location

## 🔧 Environment Variables

The scripts automatically set these environment variables in Cloud Run:

- `DATABASE_TYPE=firestore` - Uses Firestore instead of SQLite
- `GOOGLE_CLOUD_PROJECT=your_project_id` - Your Google Cloud project ID

## 🎯 AI Enhancement Setup

After deployment, you can optionally add AI enhancement by setting API keys:

```bash
# Set OpenAI API key
gcloud run services update linkedin-extractor \
  --region=us-central1 \
  --set-env-vars OPENAI_API_KEY=your_openai_key

# Set Gemini API key
gcloud run services update linkedin-extractor \
  --region=us-central1 \
  --set-env-vars GEMINI_API_KEY=your_gemini_key

# Set both at once
gcloud run services update linkedin-extractor \
  --region=us-central1 \
  --set-env-vars OPENAI_API_KEY=your_openai_key,GEMINI_API_KEY=your_gemini_key
```

## 📊 Cloud Run Configuration

The scripts deploy with these optimized settings:

- **Memory**: 1GB (sufficient for AI processing)
- **CPU**: 1 vCPU
- **Timeout**: 300 seconds (5 minutes for large files)
- **Concurrency**: 80 requests per instance
- **Max Instances**: 10 (cost control)
- **Authentication**: Public access (no authentication required)

## 🚀 Deployment Examples

### Example 1: First-time deployment
```bash
# Interactive deployment
./deploy_to_cloud_run.sh
```

### Example 2: Quick deployment to specific project
```bash
./deploy_quick.sh my-linkedin-project
```

### Example 3: Custom service name and region
```bash
./deploy_quick.sh my-linkedin-project my-service us-west1
```

## 🔍 Post-Deployment

After successful deployment:

1. **Test your application** at the provided URL
2. **Monitor logs**:
   ```bash
   gcloud logs tail --project=YOUR_PROJECT_ID
   ```
3. **View service details**:
   ```bash
   gcloud run services describe linkedin-extractor --region=us-central1
   ```
4. **Update environment variables** if needed (see AI Enhancement section)

## 💰 Cost Estimation

**Cloud Run (per month):**
- **Free tier**: 2 million requests, 360,000 vCPU-seconds, 180,000 GiB-seconds
- **Beyond free**: ~$0.40 per million requests, $0.00002400 per vCPU-second

**Firestore (per month):**
- **Free tier**: 50K reads, 20K writes, 1GB storage per day
- **Beyond free**: ~$0.18 per 100K operations

**Your estimated cost**: Probably $0-10/month for light usage

## 🆘 Troubleshooting

### Common Issues:

1. **"gcloud not found"**
   - Install Google Cloud SDK
   - Add to PATH

2. **"Docker not found"**
   - Install Docker Desktop/Engine
   - Ensure Docker daemon is running

3. **"Permission denied"**
   - Run `gcloud auth login`
   - Ensure you have Cloud Run Admin role

4. **"Project not found"**
   - Check project ID spelling
   - Ensure you have access to the project

5. **"Firestore API not enabled"**
   - Script should auto-enable it
   - Manually enable: `gcloud services enable firestore.googleapis.com`

### Getting Help:

- Check Cloud Run logs: `gcloud logs tail --project=YOUR_PROJECT_ID`
- View service status: `gcloud run services describe SERVICE_NAME --region=REGION`
- Google Cloud Console: https://console.cloud.google.com/

## 🎉 Success!

Once deployed, your application will:
- ✅ **Run in production** on Google Cloud Run
- ✅ **Use Firestore** for scalable data storage
- ✅ **Support AI enhancement** (if API keys are set)
- ✅ **Auto-scale** based on traffic
- ✅ **Be accessible** from anywhere in the world

**Your LinkedIn Data Extractor is now production-ready!** 🚀

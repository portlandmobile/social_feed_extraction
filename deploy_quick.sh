#!/bin/bash

# Quick Deployment Script for LinkedIn Data Extractor
# Usage: ./deploy_quick.sh PROJECT_ID [SERVICE_NAME] [REGION]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 PROJECT_ID [SERVICE_NAME] [REGION]${NC}"
    echo "Example: $0 my-project-id linkedin-extractor us-central1"
    exit 1
fi

PROJECT_ID=$1
SERVICE_NAME=${2:-"linkedin-extractor"}
REGION=${3:-"us-central1"}

echo -e "${BLUE}🚀 Quick Deployment to Cloud Run${NC}"
echo "=================================="
echo "Project ID: $PROJECT_ID"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Database: Firestore"
echo ""

# Check if gcloud is available
if ! command -v gcloud >/dev/null 2>&1; then
    echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
    exit 1
fi

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi

# Set project
echo -e "${BLUE}📋 Setting project to: $PROJECT_ID${NC}"
gcloud config set project "$PROJECT_ID"

# Enable Firestore API if not already enabled
echo -e "${BLUE}🔥 Checking Firestore API...${NC}"
gcloud services enable firestore.googleapis.com --project="$PROJECT_ID" 2>/dev/null || echo "Firestore API already enabled"

# Deploy to Cloud Run
echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --allow-unauthenticated \
    --set-env-vars "DATABASE_TYPE=firestore,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 80 \
    --max-instances 10

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)")

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your application is running at: $SERVICE_URL${NC}"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo "1. Test your application at the URL above"
echo "2. Set AI API keys in Cloud Run environment variables if needed:"
echo "   gcloud run services update $SERVICE_NAME --region=$REGION --set-env-vars OPENAI_API_KEY=your_key,GEMINI_API_KEY=your_key"
echo "3. Monitor logs: gcloud logs tail --project=$PROJECT_ID"

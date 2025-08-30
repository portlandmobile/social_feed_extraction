#!/bin/bash

# LinkedIn Data Extractor - Cloud Run Deployment Script
# This script deploys the application to Google Cloud Run with Firestore

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate Google Cloud project
validate_project() {
    local project_id=$1
    
    if [ -z "$project_id" ]; then
        print_error "Project ID cannot be empty"
        return 1
    fi
    
    # Check if project exists and user has access
    if ! gcloud projects describe "$project_id" >/dev/null 2>&1; then
        print_error "Project '$project_id' not found or you don't have access"
        return 1
    fi
    
    print_success "Project '$project_id' validated successfully"
    return 0
}

# Function to check if Firestore is enabled
check_firestore() {
    local project_id=$1
    
    print_status "Checking if Firestore API is enabled..."
    
    if gcloud services list --enabled --filter="name:firestore.googleapis.com" --project="$project_id" | grep -q "firestore.googleapis.com"; then
        print_success "Firestore API is already enabled"
        return 0
    else
        print_warning "Firestore API is not enabled. Enabling now..."
        if gcloud services enable firestore.googleapis.com --project="$project_id"; then
            print_success "Firestore API enabled successfully"
            return 0
        else
            print_error "Failed to enable Firestore API"
            return 1
        fi
    fi
}

# Function to set environment variables
set_environment_variables() {
    local project_id=$1
    local openai_key=$2
    local gemini_key=$3
    
    print_status "Setting environment variables for Cloud Run deployment..."
    
    # Create environment variables string
    local env_vars="DATABASE_TYPE=firestore,GOOGLE_CLOUD_PROJECT=$project_id"
    
    if [ -n "$openai_key" ]; then
        env_vars="$env_vars,OPENAI_API_KEY=$openai_key"
    fi
    
    if [ -n "$gemini_key" ]; then
        env_vars="$env_vars,GEMINI_API_KEY=$gemini_key"
    fi
    
    # Export for use in deployment
    export CLOUD_RUN_ENV_VARS="$env_vars"
    
    print_success "Environment variables configured:"
    echo "  DATABASE_TYPE=firestore"
    echo "  GOOGLE_CLOUD_PROJECT=$project_id"
    if [ -n "$openai_key" ]; then
        echo "  OPENAI_API_KEY=[SET]"
    fi
    if [ -n "$gemini_key" ]; then
        echo "  GEMINI_API_KEY=[SET]"
    fi
    
    return 0
}

# Function to deploy to Cloud Run
deploy_to_cloud_run() {
    local project_id=$1
    local service_name=$2
    local region=$3
    
    print_status "Deploying to Google Cloud Run..."
    print_status "Service: $service_name"
    print_status "Region: $region"
    print_status "Project: $project_id"
    
    # Build and deploy
    if gcloud run deploy "$service_name" \
        --source . \
        --platform managed \
        --region "$region" \
        --project "$project_id" \
        --allow-unauthenticated \
        --set-env-vars "$CLOUD_RUN_ENV_VARS" \
        --memory 1Gi \
        --cpu 1 \
        --timeout 300 \
        --concurrency 80 \
        --max-instances 10; then
        
        print_success "Deployment completed successfully!"
        
        # Get the service URL
        local service_url=$(gcloud run services describe "$service_name" --region="$region" --project="$project_id" --format="value(status.url)")
        print_success "Your application is now running at: $service_url"
        
        return 0
    else
        print_error "Deployment failed"
        return 1
    fi
}

# Main deployment function
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  LinkedIn Data Extractor Deployment${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command_exists gcloud; then
        print_error "gcloud CLI is not installed. Please install Google Cloud SDK first."
        print_status "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
    
    # Check if user is authenticated
    print_status "Checking Google Cloud authentication..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_warning "You are not authenticated with Google Cloud"
        print_status "Please run: gcloud auth login"
        exit 1
    fi
    
    print_success "Google Cloud authentication verified"
    
    # Get project ID
    local current_project=$(gcloud config get-value project 2>/dev/null)
    local project_id=""
    
    if [ -n "$current_project" ]; then
        echo ""
        print_status "Current project: $current_project"
        read -p "Use this project? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            project_id="$current_project"
        fi
    fi
    
    if [ -z "$project_id" ]; then
        echo ""
        read -p "Enter your Google Cloud Project ID: " project_id
    fi
    
    # Validate project
    if ! validate_project "$project_id"; then
        exit 1
    fi
    
    # Set project
    gcloud config set project "$project_id"
    print_success "Project set to: $project_id"
    
    # Check Firestore
    if ! check_firestore "$project_id"; then
        exit 1
    fi
    
    # Get service configuration
    echo ""
    print_status "Service Configuration"
    echo "========================"
    
    local service_name="linkedin-extractor"
    read -p "Service name [$service_name]: " input_service_name
    service_name=${input_service_name:-$service_name}
    
    local region="us-central1"
    read -p "Region [$region]: " input_region
    region=${input_region:-$region}
    
    # Get API keys
    echo ""
    print_status "API Keys Configuration"
    echo "========================"
    print_warning "API keys will be stored as environment variables in Cloud Run"
    
    local openai_key=""
    read -p "OpenAI API Key (leave empty to skip): " openai_key
    
    local gemini_key=""
    read -p "Gemini API Key (leave empty to skip): " gemini_key
    
    if [ -z "$openai_key" ] && [ -z "$gemini_key" ]; then
        print_warning "No API keys provided. AI enhancement will not work in production."
    fi
    
    # Set environment variables
    if ! set_environment_variables "$project_id" "$openai_key" "$gemini_key"; then
        exit 1
    fi
    
    # Confirm deployment
    echo ""
    print_status "Deployment Summary"
    echo "==================="
    echo "Project ID: $project_id"
    echo "Service Name: $service_name"
    echo "Region: $region"
    echo "Database: Firestore"
    echo "AI Enhancement: $([ -n "$openai_key" ] || [ -n "$gemini_key" ] && echo "Enabled" || echo "Disabled")"
    
    echo ""
    read -p "Proceed with deployment? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled"
        exit 0
    fi
    
    # Deploy
    if deploy_to_cloud_run "$project_id" "$service_name" "$region"; then
        echo ""
        print_success "🎉 Deployment completed successfully!"
        echo ""
        print_status "Next steps:"
        echo "1. Test your application at the URL provided above"
        echo "2. Monitor logs: gcloud logs tail --project=$project_id"
        echo "3. View service: gcloud run services describe $service_name --region=$region"
        echo ""
        print_status "Your application is now running in production with Firestore!"
    else
        print_error "Deployment failed. Check the error messages above."
        exit 1
    fi
}

# Run main function
main "$@"

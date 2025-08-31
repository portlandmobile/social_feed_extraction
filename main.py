#!/usr/bin/env python3
"""
Main entry point for Cloud Run deployment
This file tells Cloud Run how to start the LinkedIn Data Extraction application
"""

import os
from dotenv import load_dotenv
from web_interface import app

# Load environment variables
load_dotenv()

# For Cloud Run, we just need to export the app
# The container runtime will handle starting it
# This file serves as the entry point that Cloud Run can find

#!/usr/bin/env python3
"""
Webhook service for triggering receipt processing via GitHub Actions
"""

import os
import json
import logging
import requests
from flask import Flask, request, jsonify
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')  # e.g., 'username/repo-name'
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "receipt-processing-webhook",
        "config": {
            "github_repo": GITHUB_REPO,
            "github_token_set": bool(GITHUB_TOKEN)
        }
    })

@app.route('/webhook/process-receipts', methods=['POST'])
def process_receipts():
    """
    Webhook endpoint to trigger receipt processing
    
    Expected payload:
    {
        "docupanda_id": "abc123",
        "vendor_name": "Walmart",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    """
    try:
        # Get the payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({"error": "No payload provided"}), 400
            
        docupanda_id = payload.get('docupanda_id')
        if not docupanda_id:
            return jsonify({"error": "docupanda_id is required"}), 400
            
        logger.info(f"📥 Received webhook for docupanda_id: {docupanda_id}")
        
        # Trigger GitHub Action
        github_payload = {
            "event_type": "process_receipts",
            "client_payload": {
                "docupanda_id": docupanda_id,
                "vendor_name": payload.get('vendor_name', 'Unknown'),
                "timestamp": payload.get('timestamp', datetime.now().isoformat()),
                "webhook_source": "receipt-processing-service"
            }
        }
        
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Receipt-Processing-Webhook"
        }
        
        response = requests.post(GITHUB_API_URL, json=github_payload, headers=headers)
        
        if response.status_code == 204:
            logger.info(f"✅ Successfully triggered GitHub Action for docupanda_id: {docupanda_id}")
            return jsonify({
                "status": "success",
                "message": f"Processing triggered for docupanda_id: {docupanda_id}",
                "github_action_triggered": True,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            logger.error(f"❌ Failed to trigger GitHub Action: {response.status_code} - {response.text}")
            return jsonify({
                "status": "error",
                "message": "Failed to trigger processing",
                "github_response": response.text
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/webhook/status/<docupanda_id>', methods=['GET'])
def get_status(docupanda_id):
    """Get processing status for a specific docupanda_id"""
    # This would typically query your database or GitHub Actions status
    # For now, returning a placeholder
    return jsonify({
        "docupanda_id": docupanda_id,
        "status": "processing",
        "message": "Check GitHub Actions for detailed status",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Validate required environment variables
    if not GITHUB_TOKEN:
        logger.error("❌ GITHUB_TOKEN environment variable is required")
        exit(1)
        
    if not GITHUB_REPO:
        logger.error("❌ GITHUB_REPO environment variable is required")
        exit(1)
    
    logger.info(f"🚀 Starting webhook service for repo: {GITHUB_REPO}")
    logger.info("📡 Webhook endpoints:")
    logger.info("   POST /webhook/process-receipts - Trigger processing")
    logger.info("   GET  /webhook/status/<id> - Check status")
    logger.info("   GET  /health - Health check")
    
    # Run the service
    app.run(host='0.0.0.0', port=5000, debug=False)

# 🚀 GitHub Actions Webhook Service Setup Guide

## 📋 Overview
This setup provides a **serverless webhook service** that runs entirely on GitHub Actions. External systems can trigger receipt processing by calling GitHub's API directly, eliminating the need for a separate webhook server.

## 🏗️ Architecture
```
External System → GitHub API → GitHub Actions → Receipt Processing
     ↓              ↓              ↓              ↓
  Payload      Repository      Workflow      Your Script
  (POST)       Dispatch       (Actions)     (bin/run.py)
```

## 🔧 Setup Steps

### 1. GitHub Repository Setup

#### Create GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `workflow`
4. Copy the token (you'll need it for external systems)

#### Add Repository Secrets
In your GitHub repo, go to Settings → Secrets and variables → Actions, and add:

**Database Configuration:**
- `DB_NAME`: Your database name (e.g., postgres)
- `DB_USER`: Your database username (e.g., postgres)
- `DB_PASSWORD`: Your database password
- `DB_HOST`: Your database host IP/domain
- `DB_PORT`: Your database port (e.g., 5432)

**OpenAI Configuration:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Your OpenAI model (e.g., gpt-4o-mini)

**Application Settings:**
- `MAX_CANDIDATES`: Maximum candidates to consider (e.g., 4)
- `RESULTS_DIR`: Results directory path (e.g., data/results)

### 2. Environment Variables (for local testing)
Create a `.env` file in your project root for local testing:
```bash
# GitHub Configuration (for local testing)
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=yourusername/your-repo-name
```

### 3. Install Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Using the Webhook Service

### Option 1: Direct GitHub API Call (Recommended)
External systems can call GitHub's API directly:

**Endpoint:** `https://api.github.com/repos/{owner}/{repo}/dispatches`

**Headers:**
```
Authorization: token ghp_your_token_here
Accept: application/vnd.github.v3+json
```

**Payload:**
```json
{
  "event_type": "process_receipts",
  "client_payload": {
    "docupanda_id": "abc123",
    "vendor_name": "Walmart"
  }
}
```

### Option 2: Use the Provided Client Script
```bash
# Test locally
python bin/call_github_webhook.py abc123 Walmart

# Or with just the ID
python bin/call_github_webhook.py abc123
```

### Option 3: Manual GitHub Actions Trigger
1. Go to your repo → Actions tab
2. Click "Receipt Processing Webhook Service"
3. Click "Run workflow"
4. Enter the `docupanda_id` and optional `vendor_name`
5. Click "Run workflow"

## 📡 API Endpoints

### GitHub Repository Dispatch
**URL:** `POST https://api.github.com/repos/{owner}/{repo}/dispatches`

**Request Body:**
```json
{
  "event_type": "process_receipts",
  "client_payload": {
    "docupanda_id": "abc123",
    "vendor_name": "Walmart",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

**Response:** HTTP 204 (No Content) on success

## 🔄 How It Works

1. **External system** sends POST request to GitHub's repository dispatch API
2. **GitHub** receives the request and validates the token
3. **GitHub Actions** workflow starts automatically
4. **Workflow** extracts `docupanda_id` from the payload
5. **Processing** runs your `bin/run.py` script with the provided ID
6. **Results** are saved to your database
7. **Workflow** completes and logs the results

## 🚀 Benefits of This Approach

- ✅ **100% Serverless** - No servers to manage
- ✅ **Always Available** - GitHub Actions runs 24/7
- ✅ **Highly Scalable** - Can handle unlimited concurrent requests
- ✅ **Cost-Effective** - GitHub Actions are free for public repos
- ✅ **Professional** - Enterprise-grade reliability
- ✅ **Integrated** - Everything runs in one place

## 🔍 Monitoring & Debugging

### Check GitHub Actions
- Go to your repo → Actions tab
- Look for "Receipt Processing Webhook Service" workflow runs
- Check logs for any errors
- View step summaries for webhook information

### Test the Webhook
```bash
# Test with the client script
python bin/call_github_webhook.py test123

# Check workflow status
# Go to Actions tab in your GitHub repo
```

### Test Individual Components
```bash
# Test processing directly
python bin/run.py --docupanda_id test123 --dry_run

# Check database
python -c "from app.database.queries import get_receipt_items_by_docupanda_id; print(get_receipt_items_by_docupanda_id('test123'))"
```

## 🚨 Troubleshooting

### Common Issues

1. **"GITHUB_TOKEN environment variable is required"**
   - Set `GITHUB_TOKEN` in your `.env` file for local testing
   - Ensure external systems use valid GitHub tokens

2. **"Failed to trigger workflow: 401"**
   - Check your GitHub token has correct permissions (`repo`, `workflow`)
   - Ensure token hasn't expired

3. **"Failed to trigger workflow: 404"**
   - Check repository name format is correct
   - Ensure repo exists and is accessible

4. **Database connection errors in GitHub Actions**
   - Verify all database secrets are set in GitHub repository secrets
   - Check database host accessibility from GitHub Actions runners

5. **Workflow not starting**
   - Check the Actions tab for any workflow errors
   - Verify the `event_type` is exactly `process_receipts`

## 🔐 Security Considerations

- **GitHub Token**: Keep your personal access token secure
- **Repository Access**: Only give tokens to systems that need them
- **Database Credentials**: Store securely in GitHub secrets
- **Rate Limiting**: GitHub has rate limits for API calls

## 📈 Scaling Considerations

- **Concurrent Workflows**: GitHub Actions can run multiple workflows simultaneously
- **Queue Management**: GitHub handles queuing automatically
- **Resource Limits**: Be aware of GitHub Actions usage limits
- **Monitoring**: Use GitHub's built-in monitoring and notifications

## 🎯 Next Steps

1. **Set up GitHub secrets** for all environment variables
2. **Test locally** with the provided client script
3. **Configure external systems** to call GitHub's API directly
4. **Monitor workflow runs** in the Actions tab
5. **Set up notifications** for workflow completion/failure

## 🌐 External System Integration

### cURL Example
```bash
curl -X POST https://api.github.com/repos/yourusername/your-repo/dispatches \
  -H "Authorization: token ghp_your_token_here" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{
    "event_type": "process_receipts",
    "client_payload": {
      "docupanda_id": "abc123",
      "vendor_name": "Walmart"
    }
  }'
```

### Python Example
```python
import requests

response = requests.post(
    "https://api.github.com/repos/yourusername/your-repo/dispatches",
    headers={
        "Authorization": "token ghp_your_token_here",
        "Accept": "application/vnd.github.v3+json"
    },
    json={
        "event_type": "process_receipts",
        "client_payload": {
            "docupanda_id": "abc123",
            "vendor_name": "Walmart"
        }
    }
)

if response.status_code == 204:
    print("✅ Webhook triggered successfully!")
else:
    print(f"❌ Failed: {response.status_code} - {response.text}")
```

This approach gives you a **production-ready, serverless webhook service** that runs entirely on GitHub's infrastructure! 🚀

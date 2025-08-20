# n8n Workflow Manager

A Python application for programmatically managing n8n workflows via REST API.

## Features

- Create workflows programmatically
- Import/export workflow JSON
- Manage workflow lifecycle (create, read, update, delete)
- CLI interface for workflow operations
- Workflow templates and generators

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your n8n configuration
```

## Usage

### Python API

```python
from n8n_client import N8NClient

# Initialize client
client = N8NClient()

# Create workflow
workflow = client.create_workflow("My Workflow", nodes=[...], connections={...})
```

### Fetching Workflows from n8n

Use the `get_workflows.py` script to fetch existing workflows from your n8n instance:

```bash
# Set up environment variables
cp env.example .env
# Edit .env with your n8n API key

# Run the script
python get_workflows.py
```

**Features:**
- 🔍 **List all workflows** from n8n instance
- 📊 **Workflow statistics** (active/inactive counts)
- 🧩 **Node type analysis** for each workflow
- 💾 **Export workflows** to JSON files
- 🔑 **API key authentication** support

## Project Structure

```
src/python/
├── n8n_client.py        # n8n Python package client
├── example.py            # Example usage script
├── get_workflows.py      # Script to fetch workflows from n8n
├── requirements.txt      # Python dependencies
├── env.example           # Environment variables template
└── README.md            # This file
```

## Environment Variables

- `N8N_URL`: n8n instance URL (default: http://localhost:5678)
- `N8N_API_KEY`: API key for authentication (**required**)
- `NGROK_URL`: Ngrok webhook URL for external access

### Getting Your n8n API Key

1. Open n8n in your browser
2. Go to **Settings** → **API**
3. Click **Create API Key**
4. Copy the generated key to your `.env` file

#!/usr/bin/env python3
"""
Example script demonstrating how to use the n8n Python package
to create and manage workflows programmatically, including
direct import to n8n.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from n8n_client import N8NClient

def import_workflow_to_n8n(workflow_data, n8n_url="http://localhost:5678", api_key=None):
    """
    Import a workflow directly into n8n.
    
    Args:
        workflow_data: Workflow dictionary or JSON file path
        n8n_url: n8n instance URL
        api_key: API key for authentication
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not api_key:
            print("❌ API key is required for n8n import")
            return False
        
        # If workflow_data is a file path, load it
        if isinstance(workflow_data, str) and os.path.exists(workflow_data):
            with open(workflow_data, 'r') as f:
                workflow_data = json.load(f)
        
        # Remove ID and timestamps for new import
        if isinstance(workflow_data, dict):
            workflow_data.pop('id', None)
            workflow_data.pop('createdAt', None)
            workflow_data.pop('updatedAt', None)
            workflow_data.pop('versionId', None)
            workflow_data.pop('webhookId', None)
            workflow_data.pop('triggerCount', None)
            workflow_data.pop('staticData', None)
            workflow_data.pop('meta', None)
            workflow_data.pop('pinData', None)
            workflow_data.pop('tags', None)
            workflow_data.pop('credentials', None)
            workflow_data.pop('active', None)
        
        headers = {'X-N8N-API-KEY': api_key, 'Content-Type': 'application/json'}
        
        # Import workflow to n8n
        response = requests.post(
            f"{n8n_url}/api/v1/workflows", 
            headers=headers, 
            json=workflow_data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        workflow_name = workflow_data.get('name', 'Unnamed')
        workflow_id = result.get('id', 'Unknown')
        
        print(f"✅ Successfully imported workflow '{workflow_name}' to n8n")
        print(f"   📋 Workflow ID: {workflow_id}")
        print(f"   🔗 View at: {n8n_url}/workflow/{workflow_id}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to import workflow to n8n: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during import: {e}")
        return False

def create_telegram_ai_workflow():
    """
    Create a workflow similar to telegram_ai_gmail_calender.json
    """
    workflow = {
        "name": "Telegram AI Gmail Calendar Assistant",
        "nodes": [
            {
                "parameters": {
                    "model": "gpt-4",
                    "options": {}
                },
                "id": "openai-model-001",
                "name": "OpenAI Model",
                "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                "typeVersion": 1,
                "position": [672, 240]
            },
            {
                "parameters": {
                    "operation": "getAll",
                    "calendar": {
                        "__rl": True,
                        "value": "user@example.com",
                        "mode": "list",
                        "cachedResultName": "user@example.com"
                    },
                    "timeMin": "={{ $fromAI('After', ``, 'string') }}",
                    "timeMax": "={{ $fromAI('Before', ``, 'string') }}",
                    "options": {}
                },
                "type": "n8n-nodes-base.googleCalendarTool",
                "typeVersion": 1.3,
                "position": [992, 256],
                "id": "calendar-tool-001",
                "name": "Get Calendar Events"
            },
            {
                "parameters": {
                    "chatId": "{{ $json.chatId }}",
                    "text": "={{ $json.output }}",
                    "additionalFields": {
                        "appendAttribution": False
                    }
                },
                "type": "n8n-nodes-base.telegram",
                "typeVersion": 1.2,
                "position": [1152, 32],
                "id": "telegram-send-001",
                "name": "Send Telegram Message",
                "executeOnce": False
            },
            {
                "parameters": {
                    "updates": ["message"],
                    "additionalFields": {}
                },
                "type": "n8n-nodes-base.telegramTrigger",
                "typeVersion": 1.2,
                "position": [576, 32],
                "id": "telegram-trigger-001",
                "name": "Telegram Trigger"
            },
            {
                "parameters": {
                    "operation": "getAll",
                    "returnAll": True,
                    "simple": "={{ $fromAI('Simplify', ``, 'boolean') }}",
                    "filters": {
                        "q": "=from:{{ $fromAI('email') }}"
                    },
                    "options": {}
                },
                "type": "n8n-nodes-base.gmailTool",
                "typeVersion": 2.1,
                "position": [1152, 240],
                "id": "gmail-tool-001",
                "name": "Get Gmail Messages"
            },
            {
                "parameters": {
                    "sessionIdType": "customKey",
                    "sessionKey": "={{ $('Telegram Trigger').item.json.message }}"
                },
                "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
                "typeVersion": 1.3,
                "position": [816, 240],
                "id": "memory-buffer-001",
                "name": "Conversation Memory"
            },
            {
                "parameters": {
                    "promptType": "define",
                    "text": "=# User message\n{{ $json.message.text }}",
                    "options": {
                        "systemMessage": "You are an expert Agent in using tools google calendar and gmail and help user on his request.\nUse today's date as reference: {{ $now}}.\n"
                    }
                },
                "type": "@n8n/n8n-nodes-langchain.agent",
                "typeVersion": 2.2,
                "position": [816, 32],
                "id": "ai-agent-001",
                "name": "AI Agent",
                "alwaysOutputData": True
            }
        ],
        "connections": {
            "OpenAI Model": {
                "ai_languageModel": [
                    [
                        {
                            "node": "AI Agent",
                            "type": "ai_languageModel",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Calendar Events": {
                "ai_tool": [
                    [
                        {
                            "node": "AI Agent",
                            "type": "ai_tool",
                            "index": 0
                        }
                    ]
                ]
            },
            "Telegram Trigger": {
                "main": [
                    [
                        {
                            "node": "AI Agent",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Gmail Messages": {
                "ai_tool": [
                    [
                        {
                            "node": "AI Agent",
                            "type": "ai_tool",
                            "index": 0
                        }
                    ]
                ]
            },
            "Conversation Memory": {
                "ai_memory": [
                    [
                        {
                            "node": "AI Agent",
                            "type": "ai_memory",
                            "index": 0
                        }
                    ]
                ]
            },
            "AI Agent": {
                "main": [
                    [
                        {
                            "node": "Send Telegram Message",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }
    
    return workflow

def main():
    """Main function demonstrating n8n workflow creation and import."""
    
    # Load environment variables
    load_dotenv()
    
    print("🚀 n8n Workflow Manager Example")
    print("=" * 40)
    
    try:
        # Initialize the n8n client
        client = N8NClient()
        
        # Create the Telegram AI workflow based on your existing workflow
        print("\n📝 Creating Telegram AI Gmail Calendar workflow...")
        telegram_ai_workflow = create_telegram_ai_workflow()
        
        # Export the workflow to JSON
        workflow_file = "telegram_ai_workflow_new.json"
        client.export_workflow(telegram_ai_workflow, workflow_file)
        print(f"✅ Telegram AI workflow created and exported to {workflow_file}!")
        
        # Show workflow structure
        print(f"\n📋 **Workflow Structure**")
        print(f"   📊 Total nodes: {len(telegram_ai_workflow['nodes'])}")
        print(f"   🔗 Connections: {len(telegram_ai_workflow['connections'])}")
        print(f"   🧩 Node types: {', '.join(set(node['type'] for node in telegram_ai_workflow['nodes']))}")
        
        # Ask if user wants to import to n8n
        print(f"\n🔧 **Import Options**")
        print("1. Import workflow to n8n")
        print("2. Skip import")
        
        try:
            import_choice = input("\nEnter your choice (1-2): ").strip()
            
            if import_choice == "1":
                # Get n8n API key from environment
                n8n_api_key = os.getenv('N8N_API_KEY')
                n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
                
                if not n8n_api_key:
                    print("❌ N8N_API_KEY environment variable not found")
                    print("💡 Set it in your .env file:")
                    print("   N8N_API_KEY=your_api_key_here")
                    print("   N8N_URL=http://localhost:5678")
                else:
                    print(f"\n📤 Importing workflow to n8n at {n8n_url}...")
                    if import_workflow_to_n8n(workflow_file, n8n_url, n8n_api_key):
                        print("🎉 Workflow successfully imported to n8n!")
                    else:
                        print("❌ Failed to import workflow to n8n")
            else:
                print("⏭️ Skipping import")
                
        except KeyboardInterrupt:
            print("\n\n👋 Import cancelled")
        except Exception as e:
            print(f"❌ Error during import: {e}")
        
        print(f"\n📁 **Generated Files**")
        print(f"- {workflow_file}")
        
        print(f"\n💡 **Next Steps**")
        print(f"1. Review the workflow in {workflow_file}")
        print(f"2. Update credentials in n8n if needed")
        print(f"3. Activate the workflow in n8n")
        print(f"4. Test with a Telegram message")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to fetch and display workflows from an n8n instance.
"""

import requests
import json
import os
import sys
from typing import List, Dict, Optional
from dotenv import load_dotenv

def get_workflows_from_n8n(base_url: str = "http://localhost:5678", api_key: Optional[str] = None) -> List[Dict]:
    """
    Fetch workflows from n8n instance.
    
    Args:
        base_url: n8n instance URL
        api_key: API key for authentication (required)
        
    Returns:
        List of workflow dictionaries
    """
    try:
        if not api_key:
            print("❌ API key is required for n8n access")
            return []
        
        headers = {'X-N8N-API-KEY': api_key}
        
        # Get all workflows
        response = requests.get(f"{base_url}/api/v1/workflows", headers=headers, timeout=10)
        response.raise_for_status()
        
        workflows = response.json()
        print(f"✅ Connected to n8n at {base_url}")
        
        # Handle different response formats
        if isinstance(workflows, dict):
            # If it's a dict, it might have a 'data' key or be paginated
            if 'data' in workflows:
                workflows_list = workflows['data']
                print(f"📋 Found {len(workflows_list)} workflows in data")
            elif 'workflows' in workflows:
                workflows_list = workflows['workflows']
                print(f"📋 Found {len(workflows_list)} workflows")
            else:
                # It might be a single workflow or have a different structure
                print(f"🔍 Response keys: {list(workflows.keys())}")
                workflows_list = [workflows]  # Treat as single workflow
                print(f"📋 Treating as single workflow")
        elif isinstance(workflows, list):
            workflows_list = workflows
            print(f"📋 Found {len(workflows_list)} workflows")
        else:
            print(f"🔍 Unexpected response format: {type(workflows)}")
            workflows_list = []
        
        return workflows_list
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to n8n: {e}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def get_workflow_by_id(base_url: str, workflow_id: str, api_key: str) -> Optional[Dict]:
    """
    Get a specific workflow by ID.
    
    Args:
        base_url: n8n instance URL
        workflow_id: Workflow ID
        api_key: API key for authentication
        
    Returns:
        Workflow dictionary or None if not found
    """
    try:
        headers = {'X-N8N-API-KEY': api_key}
        
        response = requests.get(f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers, timeout=10)
        response.raise_for_status()
        
        workflow = response.json()
        print(f"✅ Retrieved workflow: {workflow.get('name', 'Unnamed')}")
        
        return workflow
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get workflow: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_archived_workflows(base_url: str = "http://localhost:5678", api_key: str = None) -> List[Dict]:
    """
    Get only archived workflows from n8n instance.
    
    Args:
        base_url: n8n instance URL
        api_key: API key for authentication
        
    Returns:
        List of archived workflow dictionaries
    """
    try:
        if not api_key:
            print("❌ API key is required for n8n access")
            return []
        
        headers = {'X-N8N-API-KEY': api_key}
        
        # Get all workflows (n8n API doesn't support includeArchived parameter)
        response = requests.get(f"{base_url}/api/v1/workflows", headers=headers, timeout=10)
        response.raise_for_status()
        
        workflows = response.json()
        
        # Handle different response formats
        if isinstance(workflows, dict):
            if 'data' in workflows:
                workflows_list = workflows['data']
            elif 'workflows' in workflows:
                workflows_list = workflows['workflows']
            else:
                workflows_list = [workflows]
        elif isinstance(workflows, list):
            workflows_list = workflows
        else:
            workflows_list = []
        
        # Filter only archived workflows
        archived_workflows = [w for w in workflows_list if isinstance(w, dict) and w.get('isArchived', False)]
        
        print(f"✅ Connected to n8n at {base_url}")
        print(f"📋 Found {len(archived_workflows)} archived workflows")
        
        return archived_workflows
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get archived workflows: {e}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def delete_archived_workflows(base_url: str = "http://localhost:5678", api_key: str = None) -> bool:
    """
    Delete all archived workflows from n8n instance.
    
    Args:
        base_url: n8n instance URL
        api_key: API key for authentication
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not api_key:
            print("❌ API key is required for n8n access")
            return False
        
        # First, get all archived workflows
        archived_workflows = get_archived_workflows(base_url, api_key)
        
        if not archived_workflows:
            print("ℹ️  No archived workflows found to delete")
            return True
        
        print(f"⚠️  Found {len(archived_workflows)} archived workflows to delete:")
        for workflow in archived_workflows:
            print(f"   - {workflow.get('name', 'Unnamed')} (ID: {workflow.get('id', 'N/A')})")
        
        # Ask for confirmation
        confirm = input("\n🗑️  Are you sure you want to delete ALL archived workflows? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ Deletion cancelled")
            return False
        
        headers = {'X-N8N-API-KEY': api_key}
        deleted_count = 0
        failed_count = 0
        
        for workflow in archived_workflows:
            workflow_id = workflow.get('id')
            workflow_name = workflow.get('name', 'Unnamed')
            
            if not workflow_id:
                print(f"⚠️  Skipping workflow '{workflow_name}' - no ID found")
                continue
            
            try:
                response = requests.delete(f"{base_url}/api/v1/workflows/{workflow_id}", headers=headers, timeout=10)
                response.raise_for_status()
                print(f"✅ Deleted: {workflow_name}")
                deleted_count += 1
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to delete '{workflow_name}': {e}")
                failed_count += 1
            except Exception as e:
                print(f"❌ Error deleting '{workflow_name}': {e}")
                failed_count += 1
        
        print(f"\n📊 **Deletion Summary**")
        print(f"   ✅ Successfully deleted: {deleted_count}")
        print(f"   ❌ Failed to delete: {failed_count}")
        
        return failed_count == 0
        
    except Exception as e:
        print(f"❌ Error during deletion process: {e}")
        return False


def display_workflow_summary(workflow) -> None:
    """
    Display a summary of a workflow.
    
    Args:
        workflow: Workflow data (dict or string)
    """
    # Handle case where workflow might be a string
    if isinstance(workflow, str):
        print(f"\n📝 Workflow: {workflow}")
        return
    
    if not isinstance(workflow, dict):
        print(f"\n❓ Unknown workflow format: {type(workflow)}")
        return
    
    workflow_id = workflow.get('id', 'N/A')
    name = workflow.get('name', 'Unnamed')
    active = workflow.get('active', False)
    archived = workflow.get('isArchived', False)
    node_count = len(workflow.get('nodes', []))
    created_at = workflow.get('createdAt', 'N/A')
    updated_at = workflow.get('updatedAt', 'N/A')
    
    # Status icons: green for active, red for inactive, gray for archived
    if archived:
        status_icon = "⚫"
        status_text = "ARCHIVED"
    elif active:
        status_icon = "🟢"
        status_text = "ACTIVE"
    else:
        status_icon = "🔴"
        status_text = "INACTIVE"
    
    print(f"\n{status_icon} **{name}** ({status_text}) (ID: {workflow_id})")
    print(f"   📊 Nodes: {node_count}")
    print(f"   📅 Created: {created_at}")
    print(f"   🔄 Updated: {updated_at}")
    
    # Show node types
    nodes = workflow.get('nodes', [])
    if nodes:
        node_types = set(node.get('type', 'unknown') for node in nodes)
        print(f"   🧩 Node types: {', '.join(sorted(node_types))}")

def export_workflow_to_file(workflow: Dict, output_dir: str = "workflows") -> str:
    """
    Export a workflow to a JSON file.
    
    Args:
        workflow: Workflow dictionary
        output_dir: Output directory
        
    Returns:
        Path to the exported file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename from workflow name
        workflow_name = workflow.get('name', 'unnamed_workflow')
        safe_name = "".join(c for c in workflow_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        filename = f"{safe_name}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Export workflow
        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        return filepath
        
    except Exception as e:
        print(f"❌ Failed to export workflow: {e}")
        return ""

def main():
    """Main function to fetch and display workflows."""
    
    # Load environment variables
    load_dotenv()
    
    print("🚀 n8n Workflow Fetcher")
    print("=" * 40)
    
    # Get configuration from environment or use defaults
    n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
    n8n_api_key = os.getenv('N8N_API_KEY')
    
    print(f"🔗 Connecting to: {n8n_url}")
    if not n8n_api_key:
        print("❌ N8N_API_KEY environment variable is required")
        print("💡 Set it in your .env file or export it:")
        print("   export N8N_API_KEY=your_api_key_here")
        sys.exit(1)
    
    print("🔑 Using API key authentication")
    
    # Ask user what type of workflows to fetch
    print(f"\n📋 **Workflow Type**")
    print("1. Active workflows only (filtered)")
    print("2. All workflows (active + inactive + archived)")
    print("3. Archived workflows only (filtered)")
    print("4. Delete archived workflows")
    
    try:
        workflow_type = input("\nEnter your choice (1-4): ").strip()
        
        if workflow_type == "1":
            # Get all workflows and filter for active ones
            all_workflows = get_workflows_from_n8n(n8n_url, n8n_api_key)
            workflows = [w for w in all_workflows if isinstance(w, dict) and w.get('active', False) and not w.get('isArchived', False)]
        elif workflow_type == "2":
            workflows = get_workflows_from_n8n(n8n_url, n8n_api_key)
        elif workflow_type == "3":
            workflows = get_archived_workflows(n8n_url, n8n_api_key)
        elif workflow_type == "4":
            # Delete archived workflows and exit
            print("\n🗑️ **Delete Archived Workflows**")
            print("-" * 40)
            
            if delete_archived_workflows(n8n_url, n8n_api_key):
                print("✅ Successfully deleted archived workflows")
            else:
                print("❌ Failed to delete some or all archived workflows")
            sys.exit(0)
        else:
            print("❌ Invalid choice, defaulting to active workflows only")
            all_workflows = get_workflows_from_n8n(n8n_url, n8n_api_key)
            workflows = [w for w in all_workflows if isinstance(w, dict) and w.get('active', False) and not w.get('isArchived', False)]
            
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        all_workflows = get_workflows_from_n8n(n8n_url, n8n_api_key)
        workflows = [w for w in all_workflows if isinstance(w, dict) and w.get('active', False) and not w.get('isArchived', False)]
    
    if not workflows:
        print("\n❌ No workflows found or failed to connect")
        sys.exit(1)
    
    # Display workflow summaries
    print(f"\n📋 **Workflow Summary** ({len(workflows)} total)")
    print("-" * 40)
    
    active_count = 0
    archived_count = 0
    for workflow in workflows:
        display_workflow_summary(workflow)
        if isinstance(workflow, dict):
            if workflow.get('isArchived', False):
                archived_count += 1
            elif workflow.get('active', False):
                active_count += 1
    
    inactive_count = len(workflows) - active_count - archived_count
    
    print(f"\n📊 **Statistics**")
    print(f"   Total workflows: {len(workflows)}")
    print(f"   Active workflows: {active_count}")
    print(f"   Inactive workflows: {inactive_count}")
    print(f"   Archived workflows: {archived_count}")
    
    # Ask user what they want to do
    print(f"\n🔧 **Actions**")
    print("1. Export all workflows")
    print("2. Export specific workflow by ID")
    print("3. Get specific workflow details")
    print("4. Delete archived workflows")
    print("5. Skip actions")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            # Export all workflows
            print("\n📤 Exporting all workflows...")
            exported_files = []
            for workflow in workflows:
                filepath = export_workflow_to_file(workflow)
                if filepath:
                    exported_files.append(filepath)
                    print(f"✅ Exported: {workflow.get('name', 'Unnamed')} -> {filepath}")
            
            print(f"\n🎉 Successfully exported {len(exported_files)} workflows to workflows/ directory")
            
        elif choice == "2":
            # Export specific workflow
            workflow_id = input("Enter workflow ID: ").strip()
            workflow = next((w for w in workflows if w.get('id') == workflow_id), None)
            
            if workflow:
                filepath = export_workflow_to_file(workflow)
                if filepath:
                    print(f"✅ Exported workflow '{workflow.get('name')}' to {filepath}")
                else:
                    print("❌ Failed to export workflow")
            else:
                print(f"❌ Workflow with ID '{workflow_id}' not found")
                
        elif choice == "3":
            # Get specific workflow details
            workflow_id = input("Enter workflow ID: ").strip()
            workflow = get_workflow_by_id(n8n_url, workflow_id, n8n_api_key)
            
            if workflow:
                print(f"\n📋 **Workflow Details**")
                print("-" * 40)
                display_workflow_summary(workflow)
                
                # Show full workflow structure
                print(f"\n🧩 **Full Structure**")
                print(f"Nodes: {len(workflow.get('nodes', []))}")
                print(f"Connections: {len(workflow.get('connections', {}))}")
                print(f"Settings: {len(workflow.get('settings', {}))}")
                
                # Ask if they want to export this workflow
                export_choice = input("\nExport this workflow? (y/n): ").strip().lower()
                if export_choice in ['y', 'yes']:
                    filepath = export_workflow_to_file(workflow)
                    if filepath:
                        print(f"✅ Exported workflow to {filepath}")
                    else:
                        print("❌ Failed to export workflow")
            else:
                print(f"❌ Workflow with ID '{workflow_id}' not found")
                
        elif choice == "4":
            # Delete archived workflows
            print("\n🗑️ **Delete Archived Workflows**")
            print("-" * 40)
            
            if delete_archived_workflows(n8n_url, n8n_api_key):
                print("✅ Successfully deleted archived workflows")
            else:
                print("❌ Failed to delete some or all archived workflows")
                
        elif choice == "5":
            print("⏭️ Skipping actions")
            
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

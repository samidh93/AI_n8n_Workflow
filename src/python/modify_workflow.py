#!/usr/bin/env python3
"""
Modify Workflow - Script to modify existing n8n workflows by name
"""

import json
import requests
import os
import sys
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

class WorkflowModifier:
    """Class to modify existing workflows by name."""
    
    def __init__(self, base_url: str = "http://localhost:5678", api_key: str = None):
        """Initialize the workflow modifier."""
        self.base_url = base_url
        self.api_key = api_key or os.getenv('N8N_API_KEY')
        
        if not self.api_key:
            raise ValueError("N8N_API_KEY environment variable is required")
        
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def find_workflow_by_name(self, workflow_name: str) -> Optional[Dict]:
        """Find a workflow by name."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            workflows = response.json()
            
            if isinstance(workflows, dict) and 'data' in workflows:
                workflows_list = workflows['data']
            else:
                workflows_list = workflows
            
            for workflow in workflows_list:
                if workflow.get('name') == workflow_name:
                    return workflow
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get workflows: {e}")
            return None
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict) -> bool:
        """Update an existing workflow."""
        try:
            # Remove fields that can't be updated
            update_data = workflow_data.copy()
            fields_to_remove = ['id', 'createdAt', 'updatedAt', 'versionId']
            for field in fields_to_remove:
                update_data.pop(field, None)
            
            response = requests.put(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json=update_data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Successfully updated workflow: {result.get('name', 'Unnamed')}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to update workflow: {e}")
            return False
    
    def modify_node_parameter(self, workflow_name: str, node_name: str, parameter_path: str, new_value: Any) -> bool:
        """Modify a specific node parameter in a workflow by name."""
        try:
            workflow = self.find_workflow_by_name(workflow_name)
            if not workflow:
                print(f"❌ Workflow '{workflow_name}' not found")
                return False
            
            workflow_id = workflow.get('id')
            
            # Find the node by name
            node = None
            for n in workflow.get('nodes', []):
                if n.get('name') == node_name:
                    node = n
                    break
            
            if not node:
                print(f"❌ Node '{node_name}' not found in workflow '{workflow_name}'")
                return False
            
            # Navigate to the parameter using the path
            current = node.get('parameters', {})
            path_parts = parameter_path.split('.')
            
            # Navigate to the parent of the target parameter
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the new value
            current[path_parts[-1]] = new_value
            
            print(f"✅ Modified parameter '{parameter_path}' in node '{node_name}' to '{new_value}'")
            return self.update_workflow(workflow_id, workflow)
            
        except Exception as e:
            print(f"❌ Failed to modify node parameter: {e}")
            return False
    
    def change_workflow_name(self, old_name: str, new_name: str) -> bool:
        """Change the name of an existing workflow."""
        try:
            workflow = self.find_workflow_by_name(old_name)
            if not workflow:
                print(f"❌ Workflow '{old_name}' not found")
                return False
            
            workflow_id = workflow.get('id')
            workflow['name'] = new_name
            
            print(f"✅ Changing workflow name from '{old_name}' to '{new_name}'")
            return self.update_workflow(workflow_id, workflow)
            
        except Exception as e:
            print(f"❌ Failed to change workflow name: {e}")
            return False
    
    def activate_workflow(self, workflow_name: str) -> bool:
        """Activate a workflow by name."""
        try:
            workflow = self.find_workflow_by_name(workflow_name)
            if not workflow:
                print(f"❌ Workflow '{workflow_name}' not found")
                return False
            
            workflow_id = workflow.get('id')
            workflow['active'] = True
            
            print(f"✅ Activating workflow: {workflow_name}")
            return self.update_workflow(workflow_id, workflow)
            
        except Exception as e:
            print(f"❌ Failed to activate workflow: {e}")
            return False
    
    def deactivate_workflow(self, workflow_name: str) -> bool:
        """Deactivate a workflow by name."""
        try:
            workflow = self.find_workflow_by_name(workflow_name)
            if not workflow:
                print(f"❌ Workflow '{workflow_name}' not found")
                return False
            
            workflow_id = workflow.get('id')
            workflow['active'] = False
            
            print(f"✅ Deactivating workflow: {workflow_name}")
            return self.update_workflow(workflow_id, workflow)
            
        except Exception as e:
            print(f"❌ Failed to deactivate workflow: {e}")
            return False
    
    def add_node_to_workflow(self, workflow_name: str, new_node: Dict, connections: Dict) -> bool:
        """Add a new node to an existing workflow by name."""
        try:
            workflow = self.find_workflow_by_name(workflow_name)
            if not workflow:
                print(f"❌ Workflow '{workflow_name}' not found")
                return False
            
            workflow_id = workflow.get('id')
            
            # Add the new node
            workflow['nodes'].append(new_node)
            
            # Add connections
            if 'connections' not in workflow:
                workflow['connections'] = {}
            
            # Update connections
            for source_node, connection_list in connections.items():
                if source_node not in workflow['connections']:
                    workflow['connections'][source_node] = {}
                
                for output_type, targets in connection_list.items():
                    if output_type not in workflow['connections'][source_node]:
                        workflow['connections'][source_node][output_type] = []
                    
                    workflow['connections'][source_node][output_type].extend(targets)
            
            print(f"✅ Added new node '{new_node.get('name', 'Unnamed')}' to workflow '{workflow_name}'")
            return self.update_workflow(workflow_id, workflow)
            
        except Exception as e:
            print(f"❌ Failed to add node to workflow: {e}")
            return False
    
    def duplicate_workflow(self, workflow_name: str, new_name: str) -> Optional[str]:
        """Duplicate an existing workflow by name."""
        try:
            workflow = self.find_workflow_by_name(workflow_name)
            if not workflow:
                print(f"❌ Workflow '{workflow_name}' not found")
                return None
            
            # Create a copy with a new name
            new_workflow = workflow.copy()
            new_workflow['name'] = new_name
            
            # Remove fields that can't be duplicated
            fields_to_remove = ['id', 'createdAt', 'updatedAt', 'versionId', 'webhookId']
            for field in fields_to_remove:
                new_workflow.pop(field, None)
            
            # Generate new IDs for nodes
            old_to_new_ids = {}
            for node in new_workflow.get('nodes', []):
                old_id = node.get('id')
                if old_id:
                    new_id = f"{old_id}_copy"
                    old_to_new_ids[old_id] = new_id
                    node['id'] = new_id
            
            # Update connections with new node IDs
            for node_name, connections in new_workflow.get('connections', {}).items():
                for output_type, connection_list in connections.items():
                    for connection_group in connection_list:
                        for connection in connection_group:
                            if 'node' in connection and connection['node'] in old_to_new_ids:
                                connection['node'] = old_to_new_ids[connection['node']]
            
            # Create the new workflow
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/workflows",
                    headers=self.headers,
                    json=new_workflow,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                new_workflow_id = result.get('id')
                print(f"✅ Successfully duplicated workflow '{workflow_name}' to '{new_name}' (ID: {new_workflow_id})")
                return new_workflow_id
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to create duplicated workflow: {e}")
                return None
            
        except Exception as e:
            print(f"❌ Failed to duplicate workflow: {e}")
            return None
    
    def export_workflow(self, workflow_name: str, filename: str = None) -> str:
        """Export a workflow to a JSON file by name."""
        try:
            workflow = self.find_workflow_by_name(workflow_name)
            if not workflow:
                print(f"❌ Workflow '{workflow_name}' not found")
                return ""
            
            if not filename:
                safe_name = "".join(c for c in workflow_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_')
                filename = f"workflows/{safe_name}_exported.json"
            
            # Create workflows directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(workflow, f, indent=2)
            
            print(f"✅ Exported workflow '{workflow_name}' to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Failed to export workflow: {e}")
            return ""

def show_usage():
    """Show usage information."""
    print("""
🔧 Workflow Modifier - Usage Examples

Commands:
1. modify_parameter <workflow_name> <node_name> <parameter_path> <new_value>
   Example: modify_parameter "My Workflow" "OpenAI Model" "model" "gpt-4-turbo"

2. rename_workflow <old_name> <new_name>
   Example: rename_workflow "Old Name" "New Name"

3. activate_workflow <workflow_name>
   Example: activate_workflow "My Workflow"

4. deactivate_workflow <workflow_name>
   Example: deactivate_workflow "My Workflow"

5. duplicate_workflow <workflow_name> <new_name>
   Example: duplicate_workflow "Original" "Copy"

6. export_workflow <workflow_name>
   Example: export_workflow "My Workflow"

7. list_workflows
   List all available workflows

8. help
   Show this help message
""")

def main():
    """Main function to handle command line arguments."""
    
    # Load environment variables
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("🚀 Workflow Modifier")
        print("=" * 40)
        show_usage()
        return
    
    try:
        # Initialize the modifier
        modifier = WorkflowModifier()
        
        command = sys.argv[1].lower()
        
        if command == "help":
            show_usage()
            
        elif command == "list_workflows":
            print("📋 Available Workflows:")
            print("-" * 30)
            
            response = requests.get(
                f"{modifier.base_url}/api/v1/workflows",
                headers=modifier.headers,
                timeout=10
            )
            response.raise_for_status()
            workflows = response.json()
            
            if isinstance(workflows, dict) and 'data' in workflows:
                workflows_list = workflows['data']
            else:
                workflows_list = workflows
            
            for workflow in workflows_list:
                status = "🟢 ACTIVE" if workflow.get('active') else "🔴 INACTIVE"
                print(f"• {workflow.get('name', 'Unnamed')} ({status})")
        
        elif command == "modify_parameter" and len(sys.argv) == 6:
            workflow_name = sys.argv[2]
            node_name = sys.argv[3]
            parameter_path = sys.argv[4]
            new_value = sys.argv[5]
            
            modifier.modify_node_parameter(workflow_name, node_name, parameter_path, new_value)
        
        elif command == "rename_workflow" and len(sys.argv) == 4:
            old_name = sys.argv[2]
            new_name = sys.argv[3]
            
            modifier.change_workflow_name(old_name, new_name)
        
        elif command == "activate_workflow" and len(sys.argv) == 3:
            workflow_name = sys.argv[2]
            
            modifier.activate_workflow(workflow_name)
        
        elif command == "deactivate_workflow" and len(sys.argv) == 3:
            workflow_name = sys.argv[2]
            
            modifier.deactivate_workflow(workflow_name)
        
        elif command == "duplicate_workflow" and len(sys.argv) == 4:
            workflow_name = sys.argv[2]
            new_name = sys.argv[3]
            
            modifier.duplicate_workflow(workflow_name, new_name)
        
        elif command == "export_workflow" and len(sys.argv) == 3:
            workflow_name = sys.argv[2]
            
            modifier.export_workflow(workflow_name)
        
        else:
            print("❌ Invalid command or missing arguments")
            show_usage()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure N8N_API_KEY is set in your .env file")

if __name__ == "__main__":
    main()

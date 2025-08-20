"""
n8n Workflow Manager for programmatically creating and managing workflows.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowNode(BaseModel):
    """Represents a workflow node."""
    id: str
    name: str
    type: str
    typeVersion: int
    position: List[int]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    credentials: Optional[Dict[str, Any]] = None


class WorkflowConnection(BaseModel):
    """Represents a workflow connection between nodes."""
    main: List[List[Dict[str, Any]]] = Field(default_factory=list)


class WorkflowData(BaseModel):
    """Represents a complete n8n workflow data structure."""
    id: Optional[str] = None
    name: str
    active: bool = False
    nodes: List[WorkflowNode]
    connections: Dict[str, WorkflowConnection] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    staticData: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)


class N8NClient:
    """Client for working with n8n workflows programmatically."""
    
    def __init__(self):
        """Initialize the n8n client."""
        logger.info("Initialized n8n workflow manager")
    
    def create_workflow(self, name: str, nodes: List[Dict] = None, connections: Dict = None) -> Dict:
        """
        Create a new workflow data structure.
        
        Args:
            name: Name of the workflow
            nodes: List of node configurations
            connections: Node connection configurations
            
        Returns:
            Workflow data dictionary
        """
        try:
            workflow_data = {
                "name": name,
                "active": False,
                "nodes": nodes or [],
                "connections": connections or {},
                "settings": {},
                "staticData": None,
                "tags": []
            }
            
            logger.info(f"Created workflow: {name}")
            return workflow_data
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
    
    def create_webhook_workflow(self, name: str, webhook_path: str = "webhook") -> Dict:
        """
        Create a simple webhook workflow.
        
        Args:
            name: Workflow name
            webhook_path: Webhook endpoint path
            
        Returns:
            Workflow data dictionary
        """
        try:
            nodes = [
                {
                    "id": "webhook-trigger",
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": webhook_path,
                        "responseMode": "responseNode",
                        "options": {}
                    }
                },
                {
                    "id": "respond-to-webhook",
                    "name": "Respond to Webhook",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [540, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": '{"message": "Hello from n8n!"}',
                        "options": {}
                    }
                }
            ]
            
            connections = {
                "Webhook Trigger": {
                    "main": [
                        [
                            {
                                "node": "Respond to Webhook",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
            
            workflow_data = self.create_workflow(name, nodes, connections)
            logger.info(f"Created webhook workflow: {name}")
            return workflow_data
            
        except Exception as e:
            logger.error(f"Failed to create webhook workflow: {e}")
            raise
    
    def create_ai_chat_workflow(self, name: str, webhook_path: str = "chat") -> Dict:
        """
        Create an AI chat workflow.
        
        Args:
            name: Workflow name
            webhook_path: Webhook endpoint path
            
        Returns:
            Workflow data dictionary
        """
        try:
            nodes = [
                {
                    "id": "chat-webhook",
                    "name": "Chat Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": webhook_path,
                        "responseMode": "responseNode",
                        "options": {}
                    }
                },
                {
                    "id": "openai-node",
                    "name": "OpenAI",
                    "type": "n8n-nodes-base.openAi",
                    "typeVersion": 1,
                    "position": [540, 300],
                    "parameters": {
                        "authentication": "apiKey",
                        "operation": "chatCompletion",
                        "model": "gpt-3.5-turbo",
                        "messages": "={{ $json.messages }}",
                        "options": {}
                    }
                },
                {
                    "id": "ai-response",
                    "name": "AI Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [840, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ $json }}",
                        "options": {}
                    }
                }
            ]
            
            connections = {
                "Chat Webhook": {
                    "main": [
                        [
                            {
                                "node": "OpenAI",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "OpenAI": {
                    "main": [
                        [
                            {
                                "node": "AI Response",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
            
            workflow_data = self.create_workflow(name, nodes, connections)
            logger.info(f"Created AI chat workflow: {name}")
            return workflow_data
            
        except Exception as e:
            logger.error(f"Failed to create AI chat workflow: {e}")
            raise
    
    def create_calendar_workflow(self, name: str) -> Dict:
        """
        Create a calendar notification workflow.
        
        Args:
            name: Workflow name
            
        Returns:
            Workflow data dictionary
        """
        try:
            nodes = [
                {
                    "id": "calendar-node",
                    "name": "Get Calendar Events",
                    "type": "n8n-nodes-base.googleCalendar",
                    "typeVersion": 2,
                    "position": [240, 300],
                    "parameters": {
                        "operation": "getAll",
                        "calendar": "primary",
                        "options": {}
                    }
                },
                {
                    "id": "if-node",
                    "name": "Check if Event Soon",
                    "type": "n8n-nodes-base.if",
                    "typeVersion": 2,
                    "position": [540, 300],
                    "parameters": {
                        "conditions": {
                            "options": {
                                "caseSensitive": True,
                                "leftValue": "",
                                "typeValidation": "strict"
                            },
                            "conditions": [
                                {
                                    "id": "condition-1",
                                    "leftValue": "={{ $json.start.dateTime }}",
                                    "rightValue": "={{ new Date(Date.now() + 24*60*60*1000) }}",
                                    "operator": {
                                        "type": "date",
                                        "operation": "before"
                                    }
                                }
                            ],
                            "combinator": "and"
                        },
                        "options": {}
                    }
                },
                {
                    "id": "email-node",
                    "name": "Send Notification",
                    "type": "n8n-nodes-base.emailSend",
                    "typeVersion": 2,
                    "position": [840, 300],
                    "parameters": {
                        "fromEmail": "noreply@example.com",
                        "toEmail": "user@example.com",
                        "subject": "Upcoming Calendar Event",
                        "text": "You have an upcoming event tomorrow!",
                        "options": {}
                    }
                }
            ]
            
            connections = {
                "Get Calendar Events": {
                    "main": [
                        [
                            {
                                "node": "Check if Event Soon",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Check if Event Soon": {
                    "main": [
                        [
                            {
                                "node": "Send Notification",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
            
            workflow_data = self.create_workflow(name, nodes, connections)
            logger.info(f"Created calendar workflow: {name}")
            return workflow_data
            
        except Exception as e:
            logger.error(f"Failed to create calendar workflow: {e}")
            raise
    
    def export_workflow(self, workflow: Dict, output_file: str) -> bool:
        """
        Export workflow to JSON file.
        
        Args:
            workflow: Workflow data dictionary
            output_file: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(workflow, f, indent=2)
            
            logger.info(f"Exported workflow to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export workflow: {e}")
            return False
    
    def import_workflow(self, input_file: str) -> Dict:
        """
        Import workflow from JSON file.
        
        Args:
            input_file: Input JSON file path
            
        Returns:
            Workflow data dictionary
        """
        try:
            with open(input_file, 'r') as f:
                workflow_data = json.load(f)
            
            # Create workflow from imported data
            workflow = Workflow(name=workflow_data.get('name', 'Imported Workflow'))
            
            # Add nodes
            for node_data in workflow_data.get('nodes', []):
                node = Node(
                    name=node_data.get('name', 'Node'),
                    type=node_data.get('type', 'n8n-nodes-base.webhook'),
                    parameters=node_data.get('parameters', {})
                )
                workflow.add_node(node)
            
            # Add connections
            connections = workflow_data.get('connections', {})
            for from_node, to_nodes in connections.items():
                if 'main' in to_nodes:
                    for connection_list in to_nodes['main']:
                        for connection in connection_list:
                            workflow.connect(from_node, connection['node'])
            
            logger.info(f"Imported workflow: {workflow.name}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to import workflow from {input_file}: {e}")
            raise
    
    def list_workflow_types(self) -> List[str]:
        """
        Get list of available workflow types.
        
        Returns:
            List of workflow type names
        """
        return [
            "webhook",
            "ai_chat", 
            "calendar",
            "email_automation",
            "data_processing",
            "custom"
        ]

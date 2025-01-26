# AI_n8n_Workflow
intro to AI n8n Workflows 

# Install and Run 
Source: https://docs.n8n.io/hosting/installation/docker/#starting-n8n

docker volume create n8n_data

docker run --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n

navigate to localhost:5678 to start n8n.

# use template
use the demo template to get started.
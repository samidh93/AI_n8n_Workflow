# AI n8n Workflow

Introduction to AI-powered n8n workflows with automated ngrok tunneling.

## Features

- **n8n**: Powerful workflow automation platform
- **Ngrok**: Secure tunneling for webhook endpoints
- **Docker Compose**: Easy deployment and management
- **Basic Authentication**: Secure access control
- **Persistent Storage**: Data persistence across restarts

## Prerequisites

- Docker and Docker Compose installed
- Ngrok account and auth token
- OpenAI API key (for AI workflows)

## Quick Start

### 1. Environment Setup

Copy the environment template and configure it:
```bash
cp env.example .env
```

Edit `.env` with your actual values:
- `NGROK_AUTHTOKEN`: Your ngrok authentication token
- `NGROK_DOMAIN`: Your ngrok domain (e.g., `viper-valid-happily.ngrok-free.app`)
- `OPENAI_APIKEY`: Your OpenAI API key
- `WEBHOOK_URL`: Your ngrok webhook URL (e.g., `https://viper-valid-happily.ngrok-free.app`)

### 2. Create Docker Volume

```bash
docker volume create n8n_data
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Access n8n

Navigate to [http://localhost:5678](http://localhost:5678) to access n8n.

**Note:** No authentication is required by default. The service runs on HTTP port 5678.

## Docker Compose Commands

```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs n8n
docker-compose logs ngrok

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View running services
docker-compose ps

# Rebuild and start services
docker-compose up -d --build
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GENERIC_TIMEZONE` | n8n timezone | `UTC` |
| `TZ` | System timezone | `UTC` |
| `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS` | Enforce file permissions | `true` |
| `N8N_RUNNERS_ENABLED` | Enable task runners | `true` |
| `WEBHOOK_URL` | Webhook URL for external access | Required |
| `NGROK_AUTHTOKEN` | Ngrok authentication token | Required |
| `NGROK_DOMAIN` | Ngrok domain (e.g., `viper-valid-happily.ngrok-free.app`) | Required |
| `OPENAI_APIKEY` | OpenAI API key | Required |

### Ports

- **n8n**: `localhost:5678` → `container:5678`
- **ngrok**: Internal communication only (tunneling to n8n:5678)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Your Browser  │    │   External      │
│   localhost:5678│    │   Webhooks      │
└─────────┬───────┘    └─────────┬───────┘
          │                       │
          ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   n8n Service  │◄───│   ngrok Service │
│   Port 5678    │    │   Tunneling     │
└─────────────────┘    └─────────────────┘
```

## Getting Started with Workflows

1. **Import Template**: Use the demo template in `Demo__My_first_AI_Agent_in_n8n.json`
2. **Configure Credentials**: Set up your OpenAI API key in n8n
3. **Test Workflows**: Start with simple automation tasks
4. **Scale Up**: Build complex AI-powered workflows

## Troubleshooting

### Common Issues

**n8n container restarting:**
```bash
docker-compose logs n8n
```

**Ngrok connection issues:**
```bash
docker-compose logs ngrok
```

**Permission errors:**
```bash
docker-compose down
docker volume rm n8n_data
docker volume create n8n_data
docker-compose up -d
```

### Logs and Debugging

```bash
# Follow all logs
docker-compose logs -f

# Check container status
docker-compose ps

# Inspect specific container
docker-compose exec n8n env
```

## Security Notes

- **No authentication by default** - Consider adding authentication for production use
- Keep ngrok auth tokens secure
- Regularly update Docker images
- Monitor container logs for suspicious activity
- Use HTTPS in production environments

## Support

- [n8n Documentation](https://docs.n8n.io/)
- [Ngrok Documentation](https://ngrok.com/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)

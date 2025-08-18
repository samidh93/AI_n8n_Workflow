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
- `N8N_BASIC_AUTH_PASSWORD`: Choose a secure password

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

**Default credentials:**
- Username: `admin`
- Password: Value from `N8N_BASIC_AUTH_PASSWORD` in `.env`

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
| `N8N_HOST` | n8n hostname | `localhost` |
| `N8N_PORT` | n8n port | `443` |
| `N8N_PROTOCOL` | Protocol (http/https) | `https` |
| `WEBHOOK_TUNNEL_URL` | Ngrok webhook URL | `https://localhost` |
| `N8N_BASIC_AUTH_USER` | Authentication username | `admin` |
| `N8N_BASIC_AUTH_PASSWORD` | Authentication password | `password` |
| `N8N_ENCRYPTION_KEY` | Data encryption key | Auto-generated |
| `NGROK_AUTHTOKEN` | Ngrok authentication token | Required |
| `NGROK_DOMAIN` | Ngrok domain | Required |
| `OPENAI_APIKEY` | OpenAI API key | Required |

### Ports

- **n8n**: `localhost:5678` → `container:443`
- **ngrok**: Internal communication only

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
│   Port 443     │    │   Tunneling     │
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

- Change default passwords in production
- Use strong encryption keys
- Keep ngrok auth tokens secure
- Regularly update Docker images
- Monitor container logs for suspicious activity

## Support

- [n8n Documentation](https://docs.n8n.io/)
- [Ngrok Documentation](https://ngrok.com/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)

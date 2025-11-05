# Customization Guide

Make claude-yolo work exactly how you need it. This guide covers customizing the Docker environment, using hooks, and advanced configuration.

## Philosophy

**You own `.claude-yolo/`** - Every file in this directory is yours to edit and customize. The template-based approach means you have full control over your environment.

## Quick Reference

| What to Customize | Where | Rebuild Needed? |
|-------------------|-------|-----------------|
| Add/remove tools | `.claude-yolo/Dockerfile` | Yes |
| Environment variables | `.env` | No (restart) |
| Port mappings | `.claude-yolo/docker-compose.yml` | No (restart) |
| Resource limits | `.env` | No (restart) |
| Run custom setup | `.claude-yolo/hooks/*.sh` | Depends on hook |

---

## Editing the Dockerfile

The Dockerfile defines your development environment. It's based on Ubuntu and includes common development tools.

### Location
```
.claude-yolo/Dockerfile
```

### Common Customizations

#### Add New Tools

Add tools after the main installation section:

```dockerfile
# USER CUSTOMIZATION: Add your tools here
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*
```

#### Install Language-Specific Tools

Python packages:
```dockerfile
# Install additional Python packages
RUN uv pip install --system \
    fastapi \
    sqlalchemy \
    celery \
    pandas
```

Node.js packages:
```dockerfile
# Install global npm packages
RUN npm install -g \
    typescript \
    ts-node \
    @nestjs/cli
```

Go modules:
```dockerfile
# Install Go tools
RUN go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

#### Change Base Image

Want a different Ubuntu version or distribution?

```dockerfile
# Use Ubuntu 22.04 instead of 24.04
FROM ubuntu:22.04

# Or use Debian
FROM debian:bookworm
```

#### Add Custom Directories

```dockerfile
# Create project-specific directories
RUN mkdir -p /workspace/data /workspace/cache /workspace/uploads
RUN chown -R developer:developer /workspace
```

### Best Practices

**Use markers for your changes:**
```dockerfile
# === USER CUSTOMIZATION START ===
RUN apt-get install -y my-custom-tool
# === USER CUSTOMIZATION END ===
```

**Clean up in the same RUN command:**
```dockerfile
RUN apt-get update && apt-get install -y \
    my-tool \
    && rm -rf /var/lib/apt/lists/*  # Clean up
```

**Pin versions for reproducibility:**
```dockerfile
RUN uv pip install --system \
    fastapi==0.104.1 \
    sqlalchemy==2.0.23
```

After editing:
```bash
claude-yolo build --no-cache  # Clean build
claude-yolo restart --build   # Rebuild and restart
```

---

## Using Customization Hooks

Hooks let you run custom scripts at specific points in the lifecycle without editing core files.

### Available Hooks

Located in `.claude-yolo/hooks/`:

1. **`pre-build.sh`** - Runs before building Docker image
2. **`post-build.sh`** - Runs after building Docker image
3. **`pre-start.sh`** - Runs before starting container

### Hook Template

Each hook is created with this template:

```bash
#!/bin/bash
# This hook runs [before/after] [action]
# Customize this script to fit your needs

set -e  # Exit on error

echo "Running [hook name]..."

# Your custom logic here

echo "[Hook name] complete."
```

### Example: Pre-Build Hook

Fetch secrets before building:

```bash
#!/bin/bash
# .claude-yolo/hooks/pre-build.sh

set -e

echo "Fetching build-time secrets..."

# Fetch from AWS Secrets Manager
aws secretsmanager get-secret-value \
    --secret-id my-app/build-secrets \
    --query SecretString \
    --output text > .claude-yolo/.build-secrets

echo "Secrets fetched successfully."
```

### Example: Post-Build Hook

Tag and push image:

```bash
#!/bin/bash
# .claude-yolo/hooks/post-build.sh

set -e

IMAGE_NAME="my-company/claude-yolo:latest"

echo "Tagging image as ${IMAGE_NAME}..."
docker tag claude-yolo:latest ${IMAGE_NAME}

if [ "$PUSH_TO_REGISTRY" = "true" ]; then
    echo "Pushing to registry..."
    docker push ${IMAGE_NAME}
fi

echo "Post-build tasks complete."
```

### Example: Pre-Start Hook

Validate environment:

```bash
#!/bin/bash
# .claude-yolo/hooks/pre-start.sh

set -e

echo "Validating environment..."

# Check required environment variables
required_vars=("DATABASE_URL" "API_KEY" "AWS_REGION")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set"
        exit 1
    fi
done

# Check external services
if ! curl -s --fail http://api.example.com/health > /dev/null; then
    echo "Warning: API is not reachable"
fi

echo "Environment validation complete."
```

### Making Hooks Executable

Hooks are automatically made executable by `claude-yolo init`, but if you create new ones:

```bash
chmod +x .claude-yolo/hooks/my-custom-hook.sh
```

---

## Modifying docker-compose.yml

Customize container orchestration and service configuration.

### Location
```
.claude-yolo/docker-compose.yml
```

### Common Customizations

#### Add Port Mappings

```yaml
services:
  claude-yolo:
    ports:
      - "${APP_PORT:-8000}:8000"
      - "5432:5432"  # PostgreSQL
      - "6379:6379"  # Redis
      - "3000:3000"  # Additional app port
```

#### Add Volume Mounts

```yaml
volumes:
  - ${HOST_WORKSPACE:-..}:/workspace
  - ${HOST_LOGS:-../logs}:/logs
  # Add custom mounts
  - ./data:/workspace/data
  - ~/.ssh:/home/developer/.ssh:ro
  - ~/.aws:/home/developer/.aws:ro
```

#### Add Environment Variables

```yaml
environment:
  - CLAUDE_LOG_LEVEL=${CLAUDE_LOG_LEVEL:-info}
  # Add custom variables
  - DATABASE_URL=${DATABASE_URL}
  - API_KEY=${API_KEY}
  - NODE_ENV=development
```

#### Add Service Dependencies

```yaml
services:
  claude-yolo:
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-development}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### Change Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '${CONTAINER_CPU_LIMIT:-2.0}'
      memory: ${CONTAINER_MEMORY_LIMIT:-4G}
    reservations:
      cpus: '${CONTAINER_CPU_RESERVATION:-0.5}'
      memory: ${CONTAINER_MEMORY_RESERVATION:-1G}
```

#### Add Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

After editing:
```bash
claude-yolo restart  # Apply changes
```

---

## Environment Configuration

The `.env` file controls runtime behavior without rebuilding.

### Common Variables

#### Container Settings
```bash
# Container identity
CONTAINER_NAME=my-project-claude

# Resource limits (adjust to your system)
CONTAINER_CPU_LIMIT=4.0          # 4 CPU cores
CONTAINER_MEMORY_LIMIT=8G        # 8GB RAM
CONTAINER_CPU_RESERVATION=1.0
CONTAINER_MEMORY_RESERVATION=2G
```

#### Application Settings
```bash
# Main application port
APP_PORT=8000

# Additional ports
POSTGRES_PORT=5432
REDIS_PORT=6379

# Environment
NODE_ENV=development
PYTHON_ENV=development
```

#### Logging
```bash
# Log levels: debug, info, warn, error
CLAUDE_LOG_LEVEL=debug

# Enable verbose logging
VERBOSE=true
```

#### Cloud Provider Credentials

```bash
# AWS
AWS_PROFILE=default
AWS_REGION=us-east-1

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/home/developer/.config/gcloud/credentials.json

# Azure
AZURE_CONFIG_DIR=/home/developer/.azure
```

### Loading from Files

For secrets management:

```bash
# .env
DATABASE_URL_FILE=/run/secrets/db_url

# Then in docker-compose.yml
secrets:
  db_url:
    file: ./secrets/database_url.txt
```

---

## Advanced Customization

### Multi-Stage Dockerfile

Build multiple variants from one Dockerfile:

```dockerfile
# Base stage
FROM ubuntu:24.04 AS base
RUN apt-get update && apt-get install -y common-tools

# Development stage
FROM base AS development
RUN apt-get install -y dev-tools debuggers

# Production stage
FROM base AS production
RUN apt-get install -y production-tools
# Don't include dev tools

# Default to development
FROM development
```

Build production variant:
```bash
docker build --target production -t my-app:prod .
```

### Using Docker Build Arguments

Pass arguments during build:

```dockerfile
ARG PYTHON_VERSION=3.12
ARG NODE_VERSION=20

RUN uv pip install --system python==${PYTHON_VERSION}
RUN nvm install ${NODE_VERSION}
```

Build with custom arguments:
```bash
docker build --build-arg PYTHON_VERSION=3.11 -t claude-yolo .
```

### Custom Entrypoint

Create a custom startup script:

```bash
# .claude-yolo/entrypoint.sh
#!/bin/bash
set -e

# Run migrations
if [ -f manage.py ]; then
    python manage.py migrate
fi

# Start background services
redis-server --daemonize yes

# Execute the main command
exec "$@"
```

In Dockerfile:
```dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
```

### Network Configuration

Custom network settings:

```yaml
# docker-compose.yml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access

services:
  claude-yolo:
    networks:
      - frontend
      - backend
```

---

## Upgrading Templates

When claude-yolo releases updates, you can selectively merge changes:

### Manual Merge (Current Method)

```bash
# Save your customizations
cp .claude-yolo/Dockerfile .claude-yolo/Dockerfile.custom

# Re-init to get new templates
claude-yolo init --force

# Merge your customizations back
vimdiff .claude-yolo/Dockerfile .claude-yolo/Dockerfile.custom
```

### Preserving Customizations

Use clearly marked sections:

```dockerfile
# === CLAUDE-YOLO TEMPLATE START ===
# (template content - will be updated)
# === CLAUDE-YOLO TEMPLATE END ===

# === USER CUSTOMIZATION START ===
# (your changes - preserved during updates)
RUN apt-get install -y my-custom-tools
# === USER CUSTOMIZATION END ===
```

---

## Examples by Use Case

### Data Science Setup

```dockerfile
# Install data science tools
RUN uv pip install --system \
    pandas \
    numpy \
    scikit-learn \
    jupyter \
    matplotlib \
    seaborn \
    plotly

# Install Jupyter extensions
RUN jupyter contrib nbextension install --user
```

### Web Development Setup

```dockerfile
# Install web development tools
RUN npm install -g \
    @angular/cli \
    @vue/cli \
    create-react-app \
    gatsby-cli

# Install databases
RUN apt-get install -y \
    postgresql-client \
    mysql-client \
    redis-tools
```

### DevOps/SRE Setup

```dockerfile
# Install infrastructure tools
RUN apt-get install -y \
    ansible \
    packer \
    vault

# Install cloud CLIs (already included, but showing custom config)
RUN az config set core.output=table
RUN gcloud config set core/disable_usage_reporting true
```

---

## Troubleshooting Customizations

### Build Failures

**Check syntax:**
```bash
docker build -f .claude-yolo/Dockerfile .
```

**Debug layer by layer:**
```dockerfile
# Comment out sections to find the problem
RUN echo "Testing section 1..."
# RUN problematic-command
RUN echo "Section 1 complete"
```

### Permission Issues

**Fix ownership in Dockerfile:**
```dockerfile
RUN chown -R developer:developer /workspace /logs
```

**Or in docker-compose.yml:**
```yaml
user: "${UID:-1001}:${GID:-1001}"
```

### Memory/Resource Issues

If builds fail with memory errors:

```bash
# Increase Docker Desktop resources
# Settings → Resources → Memory → 8GB+

# Or in .env
CONTAINER_MEMORY_LIMIT=2G  # Reduce if needed
```

---

## Best Practices

1. **Version control your `.claude-yolo/` directory** - Track customizations
2. **Document changes** - Add comments explaining why
3. **Test incrementally** - Make small changes, test frequently
4. **Use hooks for temporary changes** - Keep Dockerfile clean
5. **Pin versions** - Avoid "works on my machine" issues
6. **Clean up** - Remove temporary files in the same RUN command

---

## See Also

- [Quick Start Guide](quickstart.md)
- [Commands Reference](commands.md)
- [VPN Setup](vpn-setup.md)
- [Troubleshooting](troubleshooting.md)

# Claude Code YOLO Mode - Convenience Makefile
# Commands organized by scenario/use case

.PHONY: help setup build up down restart logs shell clean

# ============================================================================
# SETUP & GETTING STARTED
# ============================================================================

help: ## Show this help message
	@echo "\033[1mClaude Code YOLO Mode - Available Commands\033[0m"
	@echo ""
	@echo "\033[1mSETUP & GETTING STARTED:\033[0m"
	@grep -E '^(setup|build|info):.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "\033[1mBASIC CONTAINER MANAGEMENT:\033[0m"
	@grep -E '^(up|down|restart|shell|logs|status):.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "\033[1mREMOTE ACCESS:\033[0m"
	@grep -E '^(up-web|down-web|web-url|up-tailscale|down-tailscale|up-tailscale-web|tailscale-status|tailscale-logs|openvpn-status|openvpn-logs|cloudflared-status|cloudflared-logs|up-cloudflared|up-cloudflared-web):.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "\033[1mCORPORATE/COMPLIANCE:\033[0m"
	@grep -E '^(up-proxy|down-proxy):.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "\033[1mMAINTENANCE & TROUBLESHOOTING:\033[0m"
	@grep -E '^(rebuild|clean|clean-logs|log-commands|log-safety|log-git):.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "\033[1mADVANCED:\033[0m"
	@grep -E '^(backup-config|restore-config|reset-config|lint-dockerfile|test):.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - copy .env and create directories
	@echo "Setting up Claude YOLO environment..."
	@cp -n .env.example .env || true
	@mkdir -p logs/commands logs/claude logs/git logs/safety logs/proxy
	@mkdir -p workspace
	@echo "✅ Setup complete! Edit .env to configure, then run 'make build'"

build: ## Build the Docker image
	@echo "Building Docker image..."
	docker-compose build

info: ## Display configuration info
	@echo "Claude YOLO Configuration:"
	@echo "  Workspace: $$(grep HOST_WORKSPACE .env 2>/dev/null | cut -d= -f2 || echo './workspace')"
	@echo "  Logs:      $$(grep HOST_LOGS .env 2>/dev/null | cut -d= -f2 || echo './logs')"
	@echo "  Log Level: $$(grep CLAUDE_LOG_LEVEL .env 2>/dev/null | cut -d= -f2 || echo 'info')"


# ============================================================================
# BASIC CONTAINER MANAGEMENT (Daily Use)
# ============================================================================

up: ## Start containers in detached mode
	@echo "Starting containers..."
	docker-compose up -d
	@echo "✅ Containers started! Use 'make shell' to enter"

down: ## Stop and remove containers
	@echo "Stopping containers..."
	docker-compose down

restart: ## Restart containers
	@echo "Restarting containers..."
	docker-compose restart

shell: ## Open interactive shell in container
	docker-compose exec claude-yolo bash

logs: ## View container logs (follow mode)
	docker-compose logs -f claude-yolo

status: ## Show container status
	@docker-compose ps


# ============================================================================
# REMOTE ACCESS (Web Terminal & Tailscale)
# ============================================================================

up-web: ## Start with web terminal (browser access)
	@echo "Starting with web terminal enabled..."
	WEBTERMINAL_ENABLED=true docker-compose up -d
	@echo "✅ Containers started with web terminal!"
	@$(MAKE) web-url

down-web: ## Stop web terminal setup
	docker-compose down

web-url: ## Display web terminal URL and auth status
	@echo ""
	@echo "🌐 Web Terminal Access:"
	@echo "   http://localhost:$$(grep WEBTERMINAL_PORT .env 2>/dev/null | cut -d= -f2 || echo '7681')"
	@if grep -q "^WEBTERMINAL_AUTH=" .env 2>/dev/null; then \
		echo "   🔒 Authentication enabled"; \
	else \
		echo "   ⚠️  No authentication (localhost only!)"; \
	fi
	@echo ""

up-tailscale: ## Start with Tailscale (private network access)
	@echo "Starting with Tailscale enabled..."
	@if ! grep -q "^TS_AUTHKEY=" .env 2>/dev/null; then \
		echo "❌ Error: TS_AUTHKEY not set in .env"; \
		echo "   Get an auth key from: https://login.tailscale.com/admin/settings/keys"; \
		exit 1; \
	fi
	docker-compose up -d
	@echo "✅ Container started!"
	@echo "   Waiting for Tailscale to connect..."
	@sleep 5
	@$(MAKE) tailscale-status

down-tailscale: ## Stop container (same as 'make down')
	docker-compose down

up-tailscale-web: ## Start with Tailscale + web terminal (best of both)
	@echo "Starting with Tailscale AND web terminal..."
	@if ! grep -q "^TS_AUTHKEY=" .env 2>/dev/null; then \
		echo "❌ Error: TS_AUTHKEY not set in .env"; \
		exit 1; \
	fi
	WEBTERMINAL_ENABLED=true docker-compose up -d
	@echo "✅ Container started with Tailscale + Web Terminal!"
	@sleep 5
	@$(MAKE) tailscale-status

tailscale-status: ## Show Tailscale connection status and IP
	@echo ""
	@echo "🔗 Tailscale Status:"
	@docker exec claude-yolo tailscale status 2>/dev/null || echo "   ⚠️  Tailscale not running or still connecting..."
	@echo ""
	@TAILSCALE_IP=$$(docker exec claude-yolo tailscale ip -4 2>/dev/null); \
	HOSTNAME=$$(grep TS_HOSTNAME .env 2>/dev/null | cut -d= -f2 || echo 'claude-yolo'); \
	if [ -n "$$TAILSCALE_IP" ]; then \
		echo "💡 Access your container from anywhere on your Tailnet:"; \
		echo "   http://$${HOSTNAME}:8000 (app port)"; \
		echo "   http://$${HOSTNAME}:7681 (web terminal, if enabled)"; \
		echo "   Or use IP: http://$${TAILSCALE_IP}:8000"; \
	fi
	@echo ""

tailscale-logs: ## View Tailscale logs
	@tail -f logs/tailscale.log 2>/dev/null || echo "⚠️  No Tailscale logs yet (TS_AUTHKEY not set?)"

openvpn-status: ## Show OpenVPN connection status and IP
	@echo ""
	@echo "🔒 OpenVPN Status:"
	@if docker exec claude-yolo pgrep openvpn > /dev/null 2>&1; then \
		echo "   ✅ OpenVPN process is running"; \
		VPN_IP=$$(docker exec claude-yolo ip addr show tun0 2>/dev/null | grep "inet " | awk '{print $$2}' | cut -d/ -f1); \
		if [ -n "$$VPN_IP" ]; then \
			echo "   📍 VPN IP: $$VPN_IP"; \
			echo "   🌐 Traffic is routed through VPN"; \
		else \
			echo "   ⚠️  Process running but tun0 interface not found"; \
		fi; \
	else \
		echo "   ❌ OpenVPN is not running"; \
		if ! grep -q "^OPENVPN_CONFIG=" .env 2>/dev/null; then \
			echo "   💡 Set OPENVPN_CONFIG in .env to enable"; \
		fi; \
	fi
	@echo ""

openvpn-logs: ## View OpenVPN logs
	@tail -f logs/openvpn.log 2>/dev/null || echo "⚠️  No OpenVPN logs yet (OPENVPN_CONFIG not set?)"

up-cloudflared: ## Start with Cloudflare Tunnel (public internet access)
	@echo "Starting with Cloudflare Tunnel enabled..."
	@if ! grep -q "^CLOUDFLARED_TUNNEL_TOKEN=" .env 2>/dev/null && ! grep -q "^CLOUDFLARED_CONFIG=" .env 2>/dev/null; then \
		echo "❌ Error: Neither CLOUDFLARED_TUNNEL_TOKEN nor CLOUDFLARED_CONFIG is set in .env"; \
		echo "   Get a tunnel token from: https://one.dash.cloudflare.com/"; \
		echo "   Or create a config file in cloudflared/"; \
		exit 1; \
	fi
	docker-compose up -d
	@echo "✅ Container started!"
	@echo "   Waiting for Cloudflare Tunnel to connect..."
	@sleep 5
	@$(MAKE) cloudflared-status

up-cloudflared-web: ## Start with Cloudflare Tunnel + web terminal (public access)
	@echo "Starting with Cloudflare Tunnel AND web terminal..."
	@if ! grep -q "^CLOUDFLARED_TUNNEL_TOKEN=" .env 2>/dev/null && ! grep -q "^CLOUDFLARED_CONFIG=" .env 2>/dev/null; then \
		echo "❌ Error: Neither CLOUDFLARED_TUNNEL_TOKEN nor CLOUDFLARED_CONFIG is set"; \
		exit 1; \
	fi
	WEBTERMINAL_ENABLED=true docker-compose up -d
	@echo "✅ Container started with Cloudflare Tunnel + Web Terminal!"
	@echo "   ⚠️  IMPORTANT: Configure public hostname in Cloudflare dashboard"
	@echo "   ⚠️  SECURITY: Set WEBTERMINAL_AUTH in .env for password protection"
	@sleep 5
	@$(MAKE) cloudflared-status

cloudflared-status: ## Show Cloudflare Tunnel connection status
	@echo ""
	@echo "☁️  Cloudflare Tunnel Status:"
	@if docker exec claude-yolo pgrep cloudflared > /dev/null 2>&1; then \
		echo "   ✅ Cloudflared process is running"; \
		echo "   🌐 Your services are accessible via Cloudflare"; \
		echo "   📋 Check your Cloudflare dashboard for tunnel details:"; \
		echo "      https://one.dash.cloudflare.com/"; \
		echo ""; \
		if grep -q "^WEBTERMINAL_ENABLED=true" .env 2>/dev/null || [ "$$WEBTERMINAL_ENABLED" = "true" ]; then \
			echo "   💡 Configure your tunnel to route to localhost:7681 for web terminal"; \
		fi; \
		echo "   💡 Configure public hostnames in Cloudflare dashboard"; \
	else \
		echo "   ❌ Cloudflared is not running"; \
		if ! grep -q "^CLOUDFLARED_TUNNEL_TOKEN=" .env 2>/dev/null && ! grep -q "^CLOUDFLARED_CONFIG=" .env 2>/dev/null; then \
			echo "   💡 Set CLOUDFLARED_TUNNEL_TOKEN or CLOUDFLARED_CONFIG in .env to enable"; \
		else \
			echo "   💡 Check logs for errors: make cloudflared-logs"; \
		fi; \
	fi
	@echo ""

cloudflared-logs: ## View Cloudflare Tunnel logs
	@tail -f logs/cloudflared.log 2>/dev/null || echo "⚠️  No Cloudflare Tunnel logs yet (CLOUDFLARED_TUNNEL_TOKEN or CLOUDFLARED_CONFIG not set?)"


# ============================================================================
# CORPORATE/COMPLIANCE (Proxy & Logging)
# ============================================================================

up-proxy: ## Start with proxy/logging enabled
	@echo "Starting with proxy enabled..."
	@echo "⚠️  Remember to set HTTP_PROXY=http://proxy:8080 in .env for proxy to work"
	docker-compose --profile proxy up -d
	@echo "✅ Containers started with proxy!"
	@echo "   Web UI: http://localhost:8081"

down-proxy: ## Stop proxy setup
	docker-compose --profile proxy down


# ============================================================================
# MAINTENANCE & TROUBLESHOOTING
# ============================================================================

rebuild: ## Rebuild image from scratch (no cache)
	@echo "Rebuilding from scratch..."
	docker-compose build --no-cache

clean: ## Remove containers, images, and volumes
	@echo "Cleaning up..."
	docker-compose down -v
	docker rmi claude-yolo-claude-yolo 2>/dev/null || true
	@echo "✅ Cleanup complete"

clean-logs: ## Clear all logs
	@echo "Clearing logs..."
	rm -rf logs/*
	mkdir -p logs/commands logs/claude logs/git logs/safety logs/proxy
	@echo "✅ Logs cleared"

log-commands: ## View command logs (tail -f)
	@tail -f logs/commands/*.log 2>/dev/null || echo "No command logs yet"

log-safety: ## View safety logs (tail -f)
	@tail -f logs/safety/checks.log 2>/dev/null || echo "No safety logs yet"

log-git: ## View git operation logs (tail -f)
	@tail -f logs/git/operations.log 2>/dev/null || echo "No git logs yet"


# ============================================================================
# ADVANCED (Backup, Restore, Reset)
# ============================================================================

backup-config: ## Backup home directory to ./backups/
	@echo "Backing up home directory..."
	@mkdir -p backups
	@if [ -d "./home" ]; then \
		tar czf ./backups/claude-home-$$(date +%Y%m%d-%H%M%S).tar.gz -C ./home . && \
		echo "✅ Backup created in ./backups/"; \
	else \
		echo "⚠️  No ./home directory found - nothing to backup"; \
	fi

restore-config: ## Restore config from backup (set BACKUP_FILE=path/to/file.tar.gz)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Set BACKUP_FILE=path/to/backup.tar.gz"; exit 1; fi
	@echo "Restoring configuration from $(BACKUP_FILE)..."
	@mkdir -p ./home
	tar xzf $(BACKUP_FILE) -C ./home
	@echo "✅ Configuration restored to ./home/"

reset-config: ## Reset config to defaults (DESTRUCTIVE - removes ./home directory)
	@echo "⚠️  This will delete all configuration in ./home/ (git config, custom settings)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	docker-compose down
	rm -rf ./home
	@echo "✅ Configuration reset. Run 'make up' to start fresh"

lint-dockerfile: ## Lint Dockerfile with hadolint (requires hadolint installed)
	@if command -v hadolint >/dev/null 2>&1; then \
		hadolint Dockerfile; \
	else \
		echo "⚠️  hadolint not installed. Install from: https://github.com/hadolint/hadolint"; \
	fi

test: ## Run basic build test
	@echo "Testing container build..."
	@docker-compose build >/dev/null 2>&1 && echo "✅ Build successful" || echo "❌ Build failed"

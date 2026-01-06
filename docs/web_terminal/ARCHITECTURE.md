# 🏗️ Web Terminal Architecture

**Fecha**: 2026-01-06  
**Versión**: v0.7.0-alpha  
**Stack**: ttyd + Nginx + Docker

---

## 📐 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       Internet                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │   Firewall (UFW)        │
         │   - Allow 443 (HTTPS)   │
         │   - Deny 7681 (ttyd)    │
         └────────────┬────────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │   Nginx (Reverse Proxy) │
         │   - SSL/TLS Termination │
         │   - Rate Limiting       │
         │   - Access Logs         │
         └────────────┬────────────┘
                      │ Docker Network (bridge)
                      ▼
         ┌─────────────────────────┐
         │   ttyd (Web Terminal)   │
         │   - WebSocket Server    │
         │   - HTTP Basic Auth     │
         │   - Command Logging     │
         └────────────┬────────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │   Bet-Copilot CLI       │
         │   - Python Application  │
         │   - SQLite Database     │
         │   - API Integrations    │
         └─────────────────────────┘
```

---

## 🔌 Components

### 1. Nginx (Reverse Proxy)
**Role**: Edge router, SSL termination, security layer

**Responsibilities**:
- HTTPS termination (port 443)
- HTTP → HTTPS redirect
- WebSocket proxy to ttyd
- Rate limiting (10 req/s per IP)
- Security headers (HSTS, CSP, etc.)
- Access/error logging

**Technology**:
- Nginx Alpine (latest)
- Config: `docker/nginx.conf`

**Ports**:
- External: 80, 443
- Internal: → ttyd:7681

---

### 2. ttyd (Web Terminal Server)
**Role**: Terminal multiplexer, WebSocket gateway

**Responsibilities**:
- Serve web-based terminal UI
- WebSocket communication (browser ↔ shell)
- HTTP Basic Authentication
- Session management (max 10 concurrent)
- Command execution
- Terminal emulation (xterm.js)

**Technology**:
- ttyd v1.7+ (C, WebSocket)
- Alpine Linux base

**Ports**:
- Internal: 7681
- External: via Nginx only

**Configuration**:
```bash
ttyd --port 7681 \
     --credential ${USER}:${PASS} \
     --max-clients 10 \
     --client-option fontSize=16 \
     --client-option theme='...' \
     python3 /app/main.py
```

---

### 3. Bet-Copilot CLI
**Role**: Core application

**Responsibilities**:
- User interaction (Rich CLI)
- API integrations (Odds, Football, Gemini)
- Data persistence (SQLite)
- Match analysis
- Predictions & recommendations

**Technology**:
- Python 3.10+
- Rich (CLI UI)
- aiohttp (async HTTP)
- aiosqlite (async DB)

**Data**:
- SQLite: `/data/bet_copilot.db`
- Logs: stdout/stderr → Docker logs

---

## 🌐 Network Flow

### Request Path: Browser → CLI

```
1. User opens browser
   ↓
2. HTTPS request: https://alpha.bet-copilot.com/terminal
   ↓
3. Nginx receives (port 443)
   ↓
4. Nginx checks:
   - Rate limit OK?
   - SSL cert valid?
   ↓
5. Proxy to ttyd (port 7681)
   ↓
6. ttyd checks:
   - Basic auth valid?
   - Max clients not exceeded?
   ↓
7. ttyd serves xterm.js UI
   ↓
8. Browser establishes WebSocket
   ↓
9. ttyd spawns: python3 /app/main.py
   ↓
10. User types commands
    ↓
11. Commands execute in Bet-Copilot CLI
    ↓
12. Output streams back via WebSocket
    ↓
13. Browser renders in terminal
```

### WebSocket Upgrade
```http
GET /terminal HTTP/1.1
Host: alpha.bet-copilot.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: ...
Authorization: Basic YWxwaGFfdXNlcjo=...

---

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: ...
```

---

## 📦 Docker Architecture

### Container Structure
```yaml
bet-network (bridge)
  │
  ├── nginx (nginx:alpine)
  │   ├── Port: 80, 443 → host
  │   ├── Volume: nginx.conf
  │   └── Volume: ssl/
  │
  └── ttyd (bet-copilot-ttyd:latest)
      ├── Port: 7681 (internal only)
      ├── Volume: bet_copilot.db
      └── Env: API keys, credentials
```

### Data Volumes
```
bet-data/
  └── bet_copilot.db (SQLite)

docker/ssl/
  ├── cert.pem (SSL certificate)
  └── key.pem (Private key)
```

### Build Process
```dockerfile
# Stage: Base
FROM alpine:3.19
RUN apk add ttyd python3 py3-pip

# Stage: Dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage: Application
COPY bet_copilot/ /app/bet_copilot/
COPY main.py /app/

# Stage: Runtime
EXPOSE 7681
CMD ["ttyd", "...", "python3", "/app/main.py"]
```

---

## 🔄 Data Flow

### CLI Command Execution
```
User types: "analyze Liverpool Chelsea"
  ↓
1. WebSocket → ttyd
  ↓
2. ttyd → stdin of python process
  ↓
3. Bet-Copilot CLI parses command
  ↓
4. CLI calls:
   - OddsAPIClient (get live odds)
   - FootballAPIClient (get team stats)
   - GeminiClient (AI analysis)
  ↓
5. Results stored in SQLite
  ↓
6. Rich renders output to stdout
  ↓
7. stdout → ttyd
  ↓
8. ttyd → WebSocket
  ↓
9. Browser renders (xterm.js)
```

### Database Access
```
Bet-Copilot CLI
  ↓
aiosqlite
  ↓
/data/bet_copilot.db (Docker volume)
  ↓
Host filesystem (persistence)
```

---

## 🔐 Security Layers

### Layer 1: Firewall (Host)
```bash
ufw deny 7681  # Block direct ttyd access
ufw allow 443  # HTTPS only
```

### Layer 2: Nginx
```nginx
- SSL/TLS termination
- Rate limiting (10 req/s)
- Security headers
- IP filtering (optional)
```

### Layer 3: ttyd
```bash
- HTTP Basic Auth
- Max clients limit
- Session isolation
```

### Layer 4: Docker
```yaml
- Network isolation (bridge)
- Resource limits (CPU, RAM)
- Read-only filesystem (optional)
```

### Layer 5: Application
```python
- API key validation
- Input sanitization
- SQL parameterization
```

---

## 📊 Performance Metrics

### Latency Budget
```
Browser → Nginx:      < 10ms
Nginx → ttyd:         < 5ms
ttyd → Python:        < 50ms
Python command:       100ms - 5s (depends on API)
Python → Browser:     < 100ms

Total: ~200ms - 5s
```

### Resource Usage
```
Nginx:        10-20MB RAM, <1% CPU
ttyd:         20-30MB RAM, 2-5% CPU
Bet-Copilot:  50-100MB RAM, 5-20% CPU
---
Total:        ~100-150MB RAM, 10-30% CPU
```

### Scalability
```
Single instance:  10 concurrent users (ttyd limit)
Multi-instance:   Nginx load balancer → N ttyd containers
Horizontal:       K8s deployment with auto-scaling
```

---

## 🔄 Deployment Flow

### Development
```bash
git checkout laptop/feature/web-terminal-shellinabox
./scripts/deploy_alpha.sh
# → http://localhost:7681
```

### Staging
```bash
git checkout development
docker-compose build
docker-compose up -d
# → http://staging.bet-copilot.com/terminal
```

### Production
```bash
git checkout master
./scripts/generate_ssl.sh alpha.bet-copilot.com
docker-compose --profile production up -d
# → https://alpha.bet-copilot.com/terminal
```

---

## 🧪 Testing Architecture

### Unit Tests
```python
# bet_copilot/tests/test_web_terminal.py
test_ttyd_auth()
test_websocket_connection()
test_command_execution()
```

### Integration Tests
```bash
# scripts/test_deployment.sh
curl -u user:pass http://localhost:7681
curl -k https://localhost/terminal
```

### Load Tests
```bash
# Apache Bench
ab -n 1000 -c 10 -A user:pass http://localhost:7681/

# Expected: 95% < 2s
```

---

## 📈 Monitoring & Observability

### Logs
```bash
# Access logs
docker-compose logs nginx | grep /terminal

# Application logs
docker-compose logs ttyd

# Error logs
docker-compose logs | grep ERROR
```

### Metrics
```bash
# Prometheus (futuro)
ttyd_connections_total
ttyd_commands_executed_total
nginx_requests_per_second
```

### Health Checks
```yaml
# Docker Compose
healthcheck:
  test: curl -f http://localhost:7681/
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 🔮 Future Architecture

### Phase 2: Session Management
```
Redis
  ↓
ttyd (session persistence)
  ↓
Multi-instance support
```

### Phase 3: Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bet-copilot-ttyd
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: ttyd
        image: bet-copilot-ttyd:latest
```

### Phase 4: API Gateway
```
Kong/Traefik
  ↓
Multiple backends (ttyd, REST API, GraphQL)
```

---

## 📚 References

- **ttyd Architecture**: https://github.com/tsl0922/ttyd/wiki/Architecture
- **Nginx Reverse Proxy**: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- **WebSocket Protocol**: https://datatracker.ietf.org/doc/html/rfc6455
- **xterm.js**: https://xtermjs.org/

---

**Última actualización**: 2026-01-06  
**Arquitecto**: Crush AI

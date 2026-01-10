# Scripts Directory

Utility scripts for development, deployment, and maintenance.

## 🚀 Setup & Startup

### START.sh
Main entry point - starts the Bet-Copilot CLI.
```bash
./scripts/START.sh
```

### quick_start.sh
Quick setup and start for first-time users.
```bash
./scripts/quick_start.sh
```

### INSTALL_DEPS.sh
Install all Python dependencies.
```bash
./scripts/INSTALL_DEPS.sh
```

## 🔍 Diagnostics

### check_apis.py
Check API connectivity and rate limits.
```bash
python scripts/check_apis.py
```

### check_deps.py
Verify all Python dependencies are installed.
```bash
python scripts/check_deps.py
```

### verify_apis.py
Test API credentials and endpoints.
```bash
python scripts/verify_apis.py
```

### test_api_fix.sh
Test API fixes and connectivity.
```bash
./scripts/test_api_fix.sh
```

### health_check.py
Comprehensive system health check.
```bash
python scripts/health_check.py
```

## 🧪 Testing

### run_tests.sh
Run the complete test suite.
```bash
./scripts/run_tests.sh
```

## 🚢 Deployment

### deploy_alpha.sh
Deploy alpha version to staging.
```bash
./scripts/deploy_alpha.sh
```

### generate_ssl.sh
Generate SSL certificates for HTTPS.
```bash
./scripts/generate_ssl.sh
```

## 🛠️ Development

### setup.py
Project setup and configuration.
```bash
python scripts/setup.py
```

### start.py
Alternative Python-based startup script.
```bash
python scripts/start.py
```

---

**Note**: Make sure to set execute permissions:
```bash
chmod +x scripts/*.sh
```

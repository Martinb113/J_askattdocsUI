# Production Deployment Guide

Complete guide for deploying the AI Chat Application to production servers.

## 📋 Pre-Deployment Checklist

### Security
- [ ] Change default admin password
- [ ] Generate strong JWT_SECRET (`openssl rand -hex 32`)
- [ ] Set DEBUG=false
- [ ] Configure real Azure AD credentials
- [ ] Update CORS_ORIGINS to production URLs
- [ ] Enable HTTPS/TLS
- [ ] Review and harden security settings

### Configuration
- [ ] Set USE_MOCK_*=false for production APIs
- [ ] Configure real AskAT&T/AskDocs endpoints
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Set up error tracking (e.g., Sentry)

### Infrastructure
- [ ] PostgreSQL 15+ running
- [ ] Domain name configured
- [ ] SSL certificates obtained
- [ ] Firewall rules configured
- [ ] Load balancer (if needed)

---

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended for Quick Setup)

**Best for**: Single server deployment, development/staging environments

```bash
# 1. Clone repository
git clone <repository-url>
cd j_askdocs

# 2. Copy and configure environment
cp .env.example .env
# Edit .env with production values

# 3. Build and start services
docker-compose up -d

# 4. Check logs
docker-compose logs -f

# 5. Access application
# Frontend: http://your-domain
# Backend API: http://your-domain/api
# API Docs: http://your-domain/docs
```

**Services Started**:
- PostgreSQL database (port 5432)
- Backend API (port 8000)
- Frontend (port 80)

**Updating**:
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head
```

---

### Option 2: Kubernetes (Recommended for Production)

**Best for**: High availability, scalability, multiple environments

#### Prerequisites
- Kubernetes cluster (GKE, EKS, AKS, or on-premise)
- kubectl configured
- Helm 3 installed

#### 1. Create Namespace

```bash
kubectl create namespace ai-chat-prod
```

#### 2. Create Secrets

```bash
# Database credentials
kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_PASSWORD=your_secure_password \
  -n ai-chat-prod

# JWT secret
kubectl create secret generic jwt-secret \
  --from-literal=JWT_SECRET=$(openssl rand -hex 32) \
  -n ai-chat-prod

# Azure AD credentials
kubectl create secret generic azure-ad-secret \
  --from-literal=AZURE_TENANT_ID=your-tenant-id \
  --from-literal=AZURE_CLIENT_ID=your-client-id \
  --from-literal=AZURE_CLIENT_SECRET=your-client-secret \
  -n ai-chat-prod
```

#### 3. Deploy PostgreSQL

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: ai-chat-prod
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: ai_chat_db
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

#### 4. Deploy Backend

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: ai-chat-prod
spec:
  replicas: 3  # Scale as needed
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/ai-chat-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: postgresql+asyncpg://postgres:$(POSTGRES_PASSWORD)@postgres:5432/ai_chat_db
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: JWT_SECRET
        - name: AZURE_TENANT_ID
          valueFrom:
            secretKeyRef:
              name: azure-ad-secret
              key: AZURE_TENANT_ID
        # ... other env vars
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### 5. Deploy Frontend

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ai-chat-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/ai-chat-frontend:latest
        ports:
        - containerPort: 80
```

#### 6. Create Services and Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-chat-ingress
  namespace: ai-chat-prod
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - your-domain.com
    secretName: ai-chat-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

---

### Option 3: Manual Server Deployment

**Best for**: Traditional VPS/VM deployment

#### 1. Server Setup (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv postgresql-15 nginx git

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Configure PostgreSQL
sudo -u postgres psql
CREATE DATABASE ai_chat_db;
CREATE USER ai_chat WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_chat_db TO ai_chat;
\q
```

#### 2. Deploy Backend

```bash
# Clone and setup
cd /opt
sudo git clone <repository-url> ai-chat
sudo chown -R $USER:$USER ai-chat
cd ai-chat/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Edit with production values

# Run migrations
alembic upgrade head

# Seed data
python scripts/seed_data.py

# Create systemd service
sudo nano /etc/systemd/system/ai-chat-backend.service
```

**Backend systemd service**:
```ini
[Unit]
Description=AI Chat Backend
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-chat/backend
Environment="PATH=/opt/ai-chat/backend/venv/bin"
ExecStart=/opt/ai-chat/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start backend
sudo systemctl daemon-reload
sudo systemctl enable ai-chat-backend
sudo systemctl start ai-chat-backend
sudo systemctl status ai-chat-backend
```

#### 3. Deploy Frontend

```bash
cd /opt/ai-chat/frontend

# Install and build
npm install
npm run build

# Configure nginx
sudo nano /etc/nginx/sites-available/ai-chat
```

**Nginx configuration**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /opt/ai-chat/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE streaming support
        proxy_buffering off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        add_header X-Accel-Buffering no;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ai-chat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

---

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Database Security

```bash
# PostgreSQL configuration
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Allow only local connections
# local   all             all                                     peer
# host    all             all             127.0.0.1/32            scram-sha-256
```

### 3. Environment Variables

**Never commit .env files to git!**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### 4. Rate Limiting

Add to nginx config:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api {
    limit_req zone=api_limit burst=20 nodelay;
    # ... rest of config
}
```

---

## 📊 Monitoring & Logging

### 1. Application Logs

```bash
# Backend logs
sudo journalctl -u ai-chat-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost/health
```

### 3. Monitoring Tools (Optional)

- **Prometheus + Grafana**: Metrics and dashboards
- **ELK Stack**: Centralized logging
- **Sentry**: Error tracking
- **Uptime Kuma**: Uptime monitoring

---

## 🔄 Backup & Recovery

### Database Backup

```bash
# Automated daily backup script
cat > /opt/backups/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/postgres"
mkdir -p $BACKUP_DIR
pg_dump -U ai_chat ai_chat_db | gzip > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /opt/backups/backup_db.sh

# Add to crontab
crontab -e
# Add line:
0 2 * * * /opt/backups/backup_db.sh
```

### Application Backup

```bash
# Backup application files
tar -czf ai-chat-backup-$(date +%Y%m%d).tar.gz /opt/ai-chat
```

---

## 🧪 Testing Deployment

### 1. Smoke Tests

```bash
# Health checks
curl https://your-domain.com/health
curl https://your-domain.com/api/health

# API test
curl -X POST https://your-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"attid":"admin","password":"Admin123!"}'
```

### 2. Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test backend
ab -n 1000 -c 10 https://your-domain.com/api/health
```

---

## 📝 Post-Deployment

### 1. Change Default Passwords

```bash
# Login as admin and change password immediately
# Or use backend script:
cd /opt/ai-chat/backend
source venv/bin/activate
python scripts/change_admin_password.py
```

### 2. Create Production Users

- Assign appropriate roles to users
- Test role-based access control
- Verify configuration access

### 3. Monitor for Issues

- Check logs for errors
- Verify SSE streaming works
- Test both AskAT&T and AskDocs
- Confirm feedback submission

---

## 🆘 Troubleshooting

### Backend not starting
```bash
# Check logs
sudo journalctl -u ai-chat-backend -n 100

# Check database connection
psql -U ai_chat -d ai_chat_db -c "SELECT 1;"
```

### Frontend not loading
```bash
# Check nginx
sudo nginx -t
sudo systemctl status nginx

# Check files
ls -la /opt/ai-chat/frontend/dist
```

### SSE streaming issues
- Verify `X-Accel-Buffering: no` header
- Check nginx proxy_buffering is off
- Increase proxy_read_timeout

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Review this deployment guide
3. Check `FULL_PROJECT_SUMMARY.md`
4. Test with MOCK services first before real APIs

---

**Deployment Status**: All configuration files and guides ready! ✅

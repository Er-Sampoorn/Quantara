# QUANTARA Deployment Guide

## 1. Deploying on Render (`render.com`)

Quantara includes a native `render.yaml` Blueprint (Infrastructure as Code) that automatically provisions:
1. **Managed PostgreSQL Database** (`quantara-postgres`)
2. **Managed Redis Cache** (`quantara-redis`)
3. **FastAPI Backend Web Service** (`quantara-api`) via Docker
4. **Next.js Web Trading Terminal** (`quantara-web`) via Node.js

### Step-by-Step Render Deployment:

1. **Push your code to GitHub / GitLab**:
   ```bash
   git init
   git add .
   git commit -m "feat: initial Quantara deployment release"
   git remote add origin https://github.com/YOUR_USER/quantara.git
   git branch -M main
   git push -u origin main
   ```

2. **Connect to Render**:
   - Navigate to [https://dashboard.render.com/blueprints](https://dashboard.render.com/blueprints).
   - Click **"New Blueprint Instance"**.
   - Connect your GitHub repository.
   - Render will detect `render.yaml` automatically.

3. **Verify Blueprint Settings**:
   - Render will display the 4 components to be created:
     - `quantara-postgres`
     - `quantara-redis`
     - `quantara-api` (Docker runtime)
     - `quantara-web` (Node.js runtime)
   - Click **"Apply"**.

4. **Access Your Live Platform**:
   - **Frontend Terminal**: `https://quantara-web.onrender.com`
   - **API Gateway & Swagger Docs**: `https://quantara-api.onrender.com/docs`
   - **Healthcheck**: `https://quantara-api.onrender.com/api/v1/system/health`

---

## 2. Deploying with Docker Compose (VPS / AWS EC2 / DigitalOcean)

To deploy on any Ubuntu / Debian VPS:

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USER/quantara.git
cd quantara

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d --build
```

Services will be accessible on:
- **Web Terminal**: `http://YOUR_SERVER_IP:3000`
- **FastAPI API**: `http://YOUR_SERVER_IP:8000`
- **Prometheus Metrics**: `http://YOUR_SERVER_IP:9090`

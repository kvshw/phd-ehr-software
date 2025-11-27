# Install AI Dependencies - Commands

## Quick Install (Recommended - Fastest)

Install dependencies directly in running containers. Run these commands from the **project root directory**:

```bash
# Navigate to project root
cd /Users/kavee/Projects/PhD/Medical\ EHR\ Software

# Install in Diagnosis Helper Service
docker exec -it ehr-diagnosis-helper-service pip install transformers torch torchvision lightgbm

# Install in Vital Risk Service
docker exec -it ehr-vital-risk-service pip install transformers torch torchvision lightgbm

# Install in Image Analysis Service
docker exec -it ehr-image-analysis-service pip install transformers torch torchvision lightgbm
```

**Time:** ~5-10 minutes per container (depends on your internet speed)

**Note:** If containers are not running, start them first:
```bash
docker compose -f devops/docker-compose.yml up -d vital-risk-service image-analysis-service diagnosis-helper-service
```

---

## Full Rebuild (Production-Ready)

Rebuild containers with dependencies baked in. Run from the **project root directory**:

```bash
# Navigate to project root
cd /Users/kavee/Projects/PhD/Medical\ EHR\ Software

# Rebuild all model services
docker compose -f devops/docker-compose.yml build --no-cache vital-risk-service image-analysis-service diagnosis-helper-service

# Restart the services
docker compose -f devops/docker-compose.yml restart vital-risk-service image-analysis-service diagnosis-helper-service
```

**Time:** ~15-30 minutes (large download for PyTorch)

---

## Verify Installation

After installation, verify the packages are installed:

```bash
# Check Diagnosis Helper
docker exec -it ehr-diagnosis-helper-service python -c "import transformers, torch, lightgbm; print('✅ All packages installed')"

# Check Vital Risk
docker exec -it ehr-vital-risk-service python -c "import transformers, torch, lightgbm; print('✅ All packages installed')"

# Check Image Analysis
docker exec -it ehr-image-analysis-service python -c "import transformers, torch, lightgbm; print('✅ All packages installed')"
```

---

## Enable AI Models

After installation, add these to your `.env` file (in project root):

```bash
# Enable AI models
USE_AI_MODEL=true
USE_ML_MODEL=true
USE_CNN_MODEL=true
```

Then restart services:

```bash
docker compose -f devops/docker-compose.yml restart vital-risk-service image-analysis-service diagnosis-helper-service
```

---

## Troubleshooting

### If containers are not running:
```bash
docker compose -f devops/docker-compose.yml up -d
```

### If you get "container not found" errors:
```bash
# List running containers
docker ps

# Start specific service
docker compose -f devops/docker-compose.yml up -d diagnosis-helper-service
```

### If installation fails:
```bash
# Check container logs
docker logs ehr-diagnosis-helper-service
docker logs ehr-vital-risk-service
docker logs ehr-image-analysis-service
```

---

## Recommended: Quick Install Method

**Run these commands in order:**

```bash
# 1. Navigate to project root
cd /Users/kavee/Projects/PhD/Medical\ EHR\ Software

# 2. Make sure containers are running
docker compose -f devops/docker-compose.yml up -d vital-risk-service image-analysis-service diagnosis-helper-service

# 3. Install dependencies (this will take 5-10 minutes per container)
docker exec -it ehr-diagnosis-helper-service pip install transformers torch torchvision lightgbm
docker exec -it ehr-vital-risk-service pip install transformers torch torchvision lightgbm
docker exec -it ehr-image-analysis-service pip install transformers torch torchvision lightgbm

# 4. Verify installation
docker exec -it ehr-diagnosis-helper-service python -c "import transformers, torch, lightgbm; print('✅ Diagnosis Helper: All packages installed')"
docker exec -it ehr-vital-risk-service python -c "import transformers, torch, lightgbm; print('✅ Vital Risk: All packages installed')"
docker exec -it ehr-image-analysis-service python -c "import transformers, torch, lightgbm; print('✅ Image Analysis: All packages installed')"

# 5. Add to .env file (or set environment variables)
echo "USE_AI_MODEL=true" >> .env
echo "USE_ML_MODEL=true" >> .env
echo "USE_CNN_MODEL=true" >> .env

# 6. Restart services
docker compose -f devops/docker-compose.yml restart vital-risk-service image-analysis-service diagnosis-helper-service
```

**That's it!** The hybrid AI system will now be active. 🚀


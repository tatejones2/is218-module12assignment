# CI/CD Pipeline - Complete Documentation

## Overview

This FastAPI Calculator API has a complete CI/CD pipeline that:

- ✅ **Runs all tests automatically** on each commit to `main` or `develop` branches
- ✅ **Scans for security vulnerabilities** using Trivy
- ✅ **Builds Docker images** on success
- ✅ **Pushes images to Docker Hub** automatically
- ✅ **Uploads test results and coverage** as artifacts
- ✅ **Handles both PR and merge** scenarios

---

## Pipeline Stages

### 1. Test Stage ✅ (Always Runs)

**Trigger**: On every push or pull request to `main` or `develop`

**Tests Run**:
```yaml
- Unit Tests
- Comprehensive Integration Tests (29 tests)
- User Endpoint Tests
- Calculation Tests
```

**Services**:
- PostgreSQL 15 (auto-started)
- Python 3.10 environment

**Outputs**:
- JUnit test reports (XML)
- Code coverage reports (HTML + XML)
- Artifact uploads (30-day retention)

**Example Output**:
```
✓ tests/unit/ - PASSED
✓ tests/integration/test_integration_comprehensive.py - 29/29 PASSED
✓ tests/integration/test_user_endpoints.py - PASSED
✓ tests/integration/test_calculation.py - PASSED
```

### 2. Security Scan ✅ (Main branch only)

**Trigger**: On successful test, when pushing to `main` branch

**Scans For**:
- Critical vulnerabilities
- High-risk security issues
- Base image vulnerabilities

**Tools**:
- Trivy (Docker image scanning)
- GitHub CodeQL (SARIF upload)

**Reports**:
- Uploaded to GitHub Security tab
- Blocks deployment on critical issues

### 3. Build & Push ✅ (Main branch only)

**Trigger**: On successful security scan, when pushing to `main` branch

**Actions**:
- ✅ Builds multi-platform Docker image (amd64, arm64)
- ✅ Logs into Docker Hub using secrets
- ✅ Generates semantic version tags
- ✅ Pushes image with cache optimization
- ✅ Creates deployment notification

**Generated Tags**:
```
your-username/is218-module12:latest          (latest version)
your-username/is218-module12:main            (branch name)
your-username/is218-module12:SHA              (commit hash)
your-username/is218-module12:main-SHORTSHA    (branch + short commit)
```

**Example**:
```
Pushed images:
- your-username/is218-module12:latest
- your-username/is218-module12:main
- your-username/is218-module12:abc1234
- your-username/is218-module12:main-abc1234
```

### 4. Deployment Notification ✅ (Success notification)

**Trigger**: On successful Docker push

**Actions**:
- ✅ Creates GitHub deployment status
- ✅ Logs deployment information
- ✅ Confirms image availability on Docker Hub

---

## Setup Instructions

### 1. Configure Docker Hub Secrets

Add these to your GitHub repository settings (`Settings > Secrets and variables > Actions`):

#### Required Secrets:
```
DOCKERHUB_USERNAME     → Your Docker Hub username
DOCKERHUB_TOKEN        → Docker Hub access token (Personal Access Token)
```

**How to get Docker Hub token**:
1. Login to [Docker Hub](https://hub.docker.com)
2. Go to Account Settings > Security
3. Click "New Access Token"
4. Create token with "Read, Write, Delete" permissions
5. Copy the token and save as GitHub secret

### 2. Repository Configuration

Ensure these exist in your repository:
```
.github/workflows/test.yml    ✅ (CI/CD pipeline)
Dockerfile                     ✅ (Docker image definition)
requirements.txt               ✅ (Python dependencies)
pytest.ini                     ✅ (Test configuration)
tests/                         ✅ (Test suite directory)
```

### 3. Branch Protection (Recommended)

In `Settings > Branches > Branch protection rules` for `main`:
- ✅ Require status checks to pass before merging
- ✅ Require code reviews before merging
- ✅ Dismiss stale pull request approvals when new commits are pushed

---

## How It Works

### Flow Diagram

```
Push to main/develop
        ↓
  [Test Stage] ─────────┐
        ↓               │
    All Pass?           │
        ↓               │
      YES              NO
        ↓               │
  [Security Scan]      Notify
        ↓               │
    All Clear?         Return
        ↓              Error
      YES
        ↓
  [Build & Push]
        ↓
   Docker Image
   Pushed to Hub
        ↓
   [Deploy Notify]
        ↓
      Success ✅
```

### Example Workflow Run

**On Push to main**:
```
1. GitHub receives push
2. Triggers workflow: ".github/workflows/test.yml"
3. Spins up Ubuntu runner
4. Starts PostgreSQL service
5. Installs Python dependencies
6. Runs all tests (unit + integration)
7. If tests pass:
   - Runs security scan
   - If no critical issues:
     - Logs into Docker Hub
     - Builds image for amd64 & arm64
     - Pushes to Docker Hub
     - Creates deployment notification
8. Uploads results as artifacts
```

---

## File Structure

```
.github/
└── workflows/
    └── test.yml              ← Main CI/CD pipeline

Dockerfile                    ← Container definition
requirements.txt              ← Python dependencies
pytest.ini                    ← Test configuration

tests/
├── unit/                     ← Unit tests
├── integration/
│   ├── test_integration_comprehensive.py  (29 tests)
│   ├── test_user_endpoints.py
│   └── test_calculation.py
└── e2e/                      ← End-to-end tests (optional)
```

---

## Key Features

### ✅ Multi-Platform Builds
- Automatically builds for Linux AMD64 and ARM64
- Enables deployment to any server type
- Uses Docker buildx for cross-platform support

### ✅ Smart Caching
```yaml
cache-from: type=registry,ref=${{ env.IMAGE_NAME }}:buildcache
cache-to: type=registry,ref=${{ env.IMAGE_NAME }}:buildcache,mode=max
```
- Speeds up builds by reusing layers
- Reduces build time on subsequent pushes
- Minimizes Docker Hub bandwidth usage

### ✅ Semantic Versioning
```yaml
type=raw,value=latest,enable={{is_default_branch}}
type=raw,value=${{ github.sha }},enable=true
```
- `latest` tag always points to most recent main branch build
- Commit SHA as tag for traceability
- Branch name as tag for easy reference

### ✅ Comprehensive Testing
```
Unit Tests                    → Isolated component tests
Integration Tests (29 tests)  → Full API workflows
User Tests                    → Authentication & authorization
Calculation Tests             → Business logic verification
```

### ✅ Security Integration
```
- Trivy scanning for vulnerabilities
- SARIF reports to GitHub Security
- Prevents deployment on critical issues
- Coverage reports for code quality
```

### ✅ Artifact Management
```
- Test results (XML format)
- Coverage reports (HTML)
- 30-day retention policy
- Easy access through GitHub Actions
```

---

## Monitoring & Debugging

### View Workflow Runs

1. Go to your GitHub repository
2. Click "Actions" tab
3. See all workflow runs with status
4. Click on a run to see detailed logs

### View Test Results

1. In workflow run, scroll to "Artifacts"
2. Download:
   - `test-results/` - JUnit XML reports
   - `coverage-report/` - HTML coverage details

### View Docker Images

1. Go to [Docker Hub](https://hub.docker.com)
2. Select your repository
3. View all pushed images with tags
4. Check image details, layers, and pull commands

### Common Issues & Solutions

#### Issue: Tests fail locally but pass in CI
**Solution**: 
- CI runs with fresh PostgreSQL
- Ensure database is initialized before tests
- Check `DATABASE_URL` environment variable

#### Issue: Docker Hub push fails
**Solution**:
- Verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets
- Confirm token has "Read, Write, Delete" permissions
- Check token expiration date

#### Issue: Security scan blocks deployment
**Solution**:
- Review Trivy scan results in GitHub Security tab
- Update base image to latest version
- Fix vulnerable dependencies in requirements.txt
- Re-push to trigger new scan

---

## Environment Variables

### During Tests
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/mytestdb
```

### During Build
```bash
REGISTRY=docker.io
IMAGE_NAME=${{ secrets.DOCKERHUB_USERNAME }}/is218-module12
```

### Required GitHub Secrets
```bash
secrets.DOCKERHUB_USERNAME  → Docker Hub username
secrets.DOCKERHUB_TOKEN     → Docker Hub access token
```

---

## Best Practices

### ✅ Do's
- ✅ Push frequently to main
- ✅ Keep tests fast (< 30 seconds ideal)
- ✅ Use meaningful commit messages
- ✅ Monitor security scan results
- ✅ Review uploaded artifacts regularly

### ❌ Don'ts
- ❌ Commit secrets/tokens to repository
- ❌ Disable security scans
- ❌ Ignore test failures
- ❌ Use weak Docker Hub tokens
- ❌ Rely solely on CI without local testing

---

## Commands for Local Testing

### Run all tests locally
```bash
docker-compose up -d
docker-compose exec web python -m pytest tests/ -v
```

### Build Docker image locally
```bash
docker build -t is218-module12:test .
```

### Test Docker image locally
```bash
docker run -d -p 8000:8000 is218-module12:test
curl http://localhost:8000/health
```

### Push test image manually
```bash
docker tag is218-module12:test your-username/is218-module12:test
docker push your-username/is218-module12:test
```

---

## Production Deployment

### Pull & Run Image
```bash
docker pull your-username/is218-module12:latest
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  your-username/is218-module12:latest
```

### Using Specific Commit
```bash
docker pull your-username/is218-module12:abc1234
docker run -d -p 8000:8000 your-username/is218-module12:abc1234
```

### Using Docker Compose
```yaml
version: '3.8'
services:
  web:
    image: your-username/is218-module12:latest
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/prod_db
    depends_on:
      - db
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: securepass
```

---

## Summary

This CI/CD pipeline ensures:

✅ **Automatic Testing** - All tests run on every commit  
✅ **Security Scanning** - Vulnerabilities caught before production  
✅ **Automated Deployment** - Docker images built and pushed on success  
✅ **Traceability** - Every image tagged with commit SHA  
✅ **Multi-Platform** - Images work on amd64 and arm64  
✅ **Fast Builds** - Smart caching minimizes build time  
✅ **Production Ready** - Fully automated, secure, reliable pipeline  

**Status**: 🟢 **COMPLETE & OPERATIONAL**

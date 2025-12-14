# CI/CD Setup - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Get Docker Hub Token (2 minutes)

1. Go to https://hub.docker.com → Sign in
2. Click your profile icon → Account Settings
3. Click "Security" → "New Access Token"
4. Name it: `github-actions`
5. Permissions: Leave all checked
6. Click "Generate"
7. **Copy the token** (you'll only see it once!)

### Step 2: Add GitHub Secrets (2 minutes)

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add Secret 1:
   - Name: `DOCKERHUB_USERNAME`
   - Value: Your Docker Hub username
5. Click **"New repository secret"**
6. Add Secret 2:
   - Name: `DOCKERHUB_TOKEN`
   - Value: The token from Step 1
7. Click **"Add secret"** for each

### Step 3: Verify Setup (1 minute)

Your repository should have these files:
- ✅ `.github/workflows/test.yml` (CI/CD pipeline)
- ✅ `Dockerfile` (Container definition)
- ✅ `requirements.txt` (Dependencies)
- ✅ `pytest.ini` (Test config)
- ✅ `tests/` directory (Test files)

---

## 🚀 What Happens on Each Push

### Push to `main` branch:
```
Push commit
    ↓
Tests run (unit + integration)
    ↓
If all tests pass:
    ↓
Security scan runs
    ↓
If no critical issues:
    ↓
Docker image built & pushed to Hub
    ↓
✅ Done!
```

### Example Workflow:
```
$ git add .
$ git commit -m "Add new feature"
$ git push origin main

[GitHub Actions]
▶ Running: Tests Stage
  ✓ Unit tests passed
  ✓ Integration tests (29/29) passed
  ✓ Coverage uploaded
  
▶ Running: Security Scan
  ✓ No critical vulnerabilities
  
▶ Running: Build & Push
  ✓ Building image for amd64
  ✓ Building image for arm64
  ✓ Pushing to Docker Hub
  
✅ Workflow complete!
   Image: your-username/is218-module12:latest
```

---

## 📊 What Gets Built & Pushed

Every successful push creates a Docker image with these tags:

```
your-username/is218-module12:latest          ← Most recent build
your-username/is218-module12:main            ← Main branch builds
your-username/is218-module12:abc1234567      ← Specific commit
```

You can then pull and run:
```bash
docker pull your-username/is218-module12:latest
docker run -p 8000:8000 your-username/is218-module12:latest
```

---

## ✅ Verify It Works

### Check Workflow Status

1. Push a commit to `main` branch
2. Go to GitHub repository → **Actions** tab
3. You should see workflow running
4. Wait for ✅ green checkmarks on all stages

### Check Docker Hub

1. Go to https://hub.docker.com
2. Go to your repository
3. Should see new image tags appearing

---

## 🛠️ Troubleshooting

### Tests fail in CI but pass locally
- Ensure `DATABASE_URL` is set correctly
- CI uses PostgreSQL running in Docker
- Check `.github/workflows/test.yml` for database config

### Docker Hub push fails
- ✅ Check secrets are added to GitHub
- ✅ Verify `DOCKERHUB_TOKEN` is not expired
- ✅ Make sure token has "Read, Write, Delete" permissions
- ✅ Check token wasn't accidentally rotated

### Image not showing up on Docker Hub
- Wait 1-2 minutes after workflow completes
- Refresh Docker Hub page
- Check workflow logs for push errors
- Verify token permissions

### Security scan blocks deployment
- Check GitHub Security tab for Trivy results
- Update base image in Dockerfile
- Fix vulnerable dependencies
- Push again to retry

---

## 📖 Full Documentation

See **CI_CD_DOCUMENTATION.md** for:
- Complete pipeline explanation
- All configuration details
- Deployment instructions
- Best practices

---

## Summary

Your CI/CD pipeline is now set up to:

✅ Run all tests automatically  
✅ Scan for security issues  
✅ Build Docker images  
✅ Push to Docker Hub  

On every push to `main` branch!

**Status**: 🟢 Ready to use

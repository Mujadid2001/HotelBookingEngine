# GitHub Actions CI/CD Setup Guide

This guide will set up automatic deployment whenever you push to `main` branch.

## Step 1: Generate SSH Key for GitHub Actions

On your **server** (as root):

```bash
# Generate SSH key for GitHub Actions
ssh-keygen -t ed25519 -f /root/.ssh/github_actions -C "github-actions"

# Display the private key (you'll need to copy this)
cat /root/.ssh/github_actions

# Add public key to authorized_keys
cat /root/.ssh/github_actions.pub >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
```

Copy the **entire private key output** (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`).

## Step 2: Add GitHub Secrets

1. Go to GitHub repository: https://github.com/mujadid2001/HotelBookingEngine
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these three secrets:

| Secret Name | Value |
|------------|-------|
| `SERVER_HOST` | `209.74.88.53` |
| `SERVER_USER` | `root` |
| `SERVER_SSH_KEY` | *Paste the entire private key from Step 1* |

## Step 3: Commit and Push

```bash
git add .github/workflows/deploy.yml
git commit -m "Add CI/CD deployment pipeline"
git push origin main
```

This will trigger the first automated deployment!

## Step 4: Monitor Deployment

1. Go to GitHub repo → **Actions** tab
2. Watch the workflow run in real-time
3. Green checkmark = successful deployment
4. Red X = deployment failed (check logs)

## Step 5: Test the Pipeline

Make any code change and push:

```bash
# Make a test change
echo "# Deployment test" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD deployment"
git push origin main
```

Watch GitHub Actions automatically deploy your changes!

## Manual Trigger

You can also manually trigger deployment without code changes:
1. Go to **Actions** tab
2. Click **Deploy to Server** workflow
3. Click **Run workflow** button

## Troubleshooting

**SSH Connection Failed:**
- Verify SERVER_HOST, SERVER_USER, SERVER_SSH_KEY are correct
- Check server SSH is running: `systemctl status sshd`

**Deployment Failed:**
- Check workflow logs in GitHub Actions tab
- SSH into server and check: `docker-compose logs web`

**Health Check Failed:**
- Ensure containers started: `docker-compose ps`
- Check app logs: `docker-compose logs web | tail -50`

## What Happens on Each Push

1. GitHub Actions checks out your code
2. Connects to server via SSH
3. Pulls latest code from GitHub
4. Rebuilds Docker images
5. Restarts containers
6. Runs migrations
7. Collects static files
8. Runs health check
9. Reports success/failure

That's it! Now deployment is automated. 🎉

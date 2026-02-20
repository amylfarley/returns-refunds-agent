# GitHub Repository Setup Guide

This guide will help you create and push this project to GitHub.

## Prerequisites

- Git installed on your machine
- GitHub account
- GitHub CLI (optional but recommended) or web browser access

## Option 1: Using GitHub CLI (Recommended)

### 1. Install GitHub CLI (if not already installed)

```bash
# macOS
brew install gh

# Linux
sudo apt install gh  # Debian/Ubuntu
sudo dnf install gh  # Fedora

# Windows
winget install --id GitHub.cli
```

### 2. Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts to authenticate.

### 3. Create Repository and Push

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Complete Returns & Refunds Agent with AgentCore"

# Create GitHub repository and push
gh repo create returns-refunds-agent --public --source=. --remote=origin --push
```

## Option 2: Using GitHub Web Interface

### 1. Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `returns-refunds-agent`
3. Description: "Production-ready AI agent for returns and refunds using AWS Bedrock AgentCore"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### 2. Push Local Code to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Complete Returns & Refunds Agent with AgentCore"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/returns-refunds-agent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Verify Your Repository

After pushing, verify that:

1. ✅ All Python scripts are present (01-15)
2. ✅ README.md displays correctly
3. ✅ Configuration files are NOT present (they're in .gitignore)
4. ✅ requirements.txt is present
5. ✅ Architecture documentation is present

## Security Check

**IMPORTANT**: Verify these sensitive files are NOT in your repository:

- ❌ cognito_config.json (contains client secret)
- ❌ memory_config.json
- ❌ gateway_config.json
- ❌ gateway_role_config.json
- ❌ lambda_config.json

These files are automatically excluded by `.gitignore`.

## Update README with Your Repository URL

After creating the repository, update the clone command in README.md:

```bash
# Replace YOUR_USERNAME with your actual GitHub username
git clone https://github.com/YOUR_USERNAME/returns-refunds-agent.git
```

Then commit and push the change:

```bash
git add README.md
git commit -m "Update repository URL in README"
git push
```

## Optional: Add Topics to Repository

On GitHub, add these topics to help others discover your project:

- `aws-bedrock`
- `agentcore`
- `strands-agents`
- `ai-agent`
- `customer-service`
- `returns-refunds`
- `lambda`
- `cognito`
- `python`

## Next Steps

1. Share your repository URL
2. Consider adding a LICENSE file
3. Add GitHub Actions for CI/CD (optional)
4. Create issues for future enhancements
5. Add a CONTRIBUTING.md if you want contributions

## Troubleshooting

### Issue: Git not initialized

```bash
git init
```

### Issue: Remote already exists

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/returns-refunds-agent.git
```

### Issue: Sensitive files accidentally committed

```bash
# Remove from git but keep locally
git rm --cached cognito_config.json
git rm --cached memory_config.json
git rm --cached gateway_config.json
git rm --cached gateway_role_config.json
git rm --cached lambda_config.json

# Commit the removal
git commit -m "Remove sensitive configuration files"
git push
```

## Support

If you encounter issues:
- Check GitHub's documentation: https://docs.github.com
- GitHub CLI documentation: https://cli.github.com/manual/
- Git documentation: https://git-scm.com/doc

---

**Ready to share your work!** 🚀

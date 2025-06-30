# GitHub Private Storage Setup Guide

This guide will help you set up the GitHub private repository storage for the SMIF Dashboard.

## Prerequisites

- GitHub account (free is fine)
- Admin access to deploy the Streamlit app

## Step 1: Create Private Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right and select "New repository"
3. Configure the repository:
   - **Repository name**: `smif-private-data` (or your preferred name)
   - **Description**: "Private data storage for SMIF Dashboard"
   - **Visibility**: **Private** (IMPORTANT!)
   - **Initialize with README**: Yes
4. Click "Create repository"

## Step 2: Generate Personal Access Token

1. Go to GitHub Settings (click your profile picture → Settings)
2. Navigate to "Developer settings" (bottom of left sidebar)
3. Click "Personal access tokens" → "Tokens (classic)"
4. Click "Generate new token" → "Generate new token (classic)"
5. Configure the token:
   - **Note**: "SMIF Dashboard Data Access"
   - **Expiration**: Set as needed (recommend 90 days with renewal reminders)
   - **Scopes**: Select only `repo` (Full control of private repositories)
6. Click "Generate token"
7. **IMPORTANT**: Copy the token immediately (it won't be shown again!)
   - Token format: `ghp_xxxxxxxxxxxxxxxxxxxx`

## Step 3: Configure Streamlit Secrets

### For Streamlit Community Cloud:

1. Go to your Streamlit app dashboard
2. Click on your app settings (⋮ menu → Settings)
3. Navigate to "Secrets" section
4. Add the following configuration:

```toml
[github]
GITHUB_TOKEN = "ghp_your_token_here"
DATA_REPO = "your-username/smif-private-data"

[emails]
ALLOWED_EMAILS = ["admin1@jhu.edu", "admin2@jhu.edu"]

[passwords]
CLASS_PASSWORD = "your_secure_password"

[settings]
APP_TITLE = "SMIF Performance Dashboard"
INITIAL_PORTFOLIO_VALUE = 338400

[class_period]
CLASS_START_DATE = "2024-09-01"
CLASS_SEMESTER = "Fall 2024"
CLASS_INITIAL_VALUE = 338400
CLASS_BENCHMARK = "VTI"
```

### For Local Development:

Create `.streamlit/secrets.toml` in your project root with the same content.

## Step 4: Test the Connection

1. Deploy or restart your Streamlit app
2. Log in with admin credentials
3. Upload test Excel files
4. Check that:
   - Upload succeeds with "saved to GitHub" message
   - Data persists after app restart
   - Files appear in your private repository

## Step 5: Verify Repository Structure

After first upload, your private repository should have:

```
smif-private-data/
├── README.md
├── metadata.json
└── data/
    ├── current/
    │   ├── README.md
    │   ├── transaction_data.xlsx
    │   └── income_data.xlsx
    └── archive/
        └── README.md
```

## Security Best Practices

1. **Token Security**:
   - Never commit tokens to code
   - Rotate tokens regularly
   - Use minimum required permissions

2. **Repository Access**:
   - Keep repository private
   - Only grant access to necessary team members
   - Review access periodically

3. **Data Protection**:
   - Don't share repository URL publicly
   - Monitor repository access logs
   - Enable 2FA on GitHub account

## Troubleshooting

### "Failed to connect to repository"
- Verify token has `repo` scope
- Check repository name format: `username/repo-name`
- Ensure repository is accessible with token

### "Failed to save to GitHub"
- Check token permissions
- Verify repository exists and is private
- Check Streamlit logs for detailed error

### "No data found in GitHub repository"
- Files haven't been uploaded yet
- Check `data/current/` directory in repository
- Clear cache and reload app

## Maintenance

### Token Renewal
1. Tokens expire based on your setting
2. Generate new token before expiration
3. Update in Streamlit secrets
4. No data migration needed

### Storage Monitoring
- GitHub free tier includes unlimited private repos
- File size limit: 100MB per file
- Repository size limit: 5GB (soft limit)

### Backup Recommendations
- GitHub automatically versions all uploads
- Consider periodic exports to local backup
- Archive old data seasonally

## Advanced Configuration

### Custom Repository Structure
Modify `github_storage.py` to change:
- Directory names
- Archive strategy
- File naming conventions

### Multiple Environments
Use different repositories for:
- Development: `smif-data-dev`
- Production: `smif-data-prod`
- Testing: `smif-data-test`

## Support

For issues with:
- **GitHub**: See [GitHub Docs](https://docs.github.com)
- **Streamlit**: See [Streamlit Docs](https://docs.streamlit.io)
- **This implementation**: Check `specs/github_private_storage_spec.md`
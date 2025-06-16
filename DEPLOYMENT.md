# SMIF Dashboard Deployment Guide

## 🚀 Quick Start - Public Repository with Streamlit Secrets

### Prerequisites
- GitHub account (public repository is fine and recommended)
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Step 1: Deploy to Streamlit Cloud

1. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your **public** repository: `jh-smif-reporting`
   - Main file path: `streamlit_app.py`
   - Click "Deploy!"

2. **Configure Secrets** (Critical Step):
   - Once deployed, go to your app's settings page
   - Click on the "Secrets" tab
   - Add the following configuration:

```toml
[emails]
ALLOWED_EMAILS = [
    "instructor@university.edu",
    "student1@university.edu", 
    "student2@university.edu",
    "student3@university.edu"
]

[passwords]
CLASS_PASSWORD = "YourSecureClassPassword2024"

[settings]
APP_TITLE = "SMIF Performance Dashboard"
INITIAL_PORTFOLIO_VALUE = 338400
```

3. **Save and Restart**: The app will automatically restart with secure authentication

### Step 2: Local Development

For local testing, edit `.streamlit/secrets.toml`:

```toml
[emails]
ALLOWED_EMAILS = [
    "your.email@university.edu"
]

[passwords]
CLASS_PASSWORD = "local_dev_password"

[settings]
APP_TITLE = "SMIF Dashboard - Local Dev"
INITIAL_PORTFOLIO_VALUE = 338400
```

Then run locally:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🔐 Secure Authentication with Email + Password

### How It Works:
- **Email-based access**: Only university emails you specify can log in
- **Shared password**: Single class password that you distribute securely
- **No exposed credentials**: All sensitive data stored in Streamlit secrets

### Adding/Removing Users:
1. Update the `ALLOWED_EMAILS` array in Streamlit Cloud secrets
2. Save the changes - app restarts automatically
3. New users can immediately access with their email + class password

### Password Management:
- Change `CLASS_PASSWORD` each semester for security
- Use strong passwords (8+ characters, mixed case, numbers, symbols)
- Distribute password securely to enrolled students only

## 📊 How to Use the Dashboard

### All Authorized Users:
1. **Login**: Use your university email + class password
2. **Upload Excel Files** (anyone can upload):
   - Investment Transaction Detail file
   - Income and Expense Detail file
3. **Generate Reports**: Click "Generate Reports" button
4. **Analyze Data**: Use interactive dashboard features:
   - Performance vs VTI benchmark
   - Portfolio allocation charts
   - Drawdown analysis
   - Data export capabilities

### Key Features:
- **Real-time Processing**: Data processed instantly, no permanent storage
- **Interactive Charts**: Performance, allocation, and drawdown visualizations  
- **Data Export**: Download as Excel, CSV, JSON, or Python pickle files
- **Jupyter Integration**: Export templates for advanced analysis

## 🔧 Customization

### Update Configuration:
Modify Streamlit Cloud secrets to:
- Add/remove authorized emails
- Change class password
- Update app title and settings
- Adjust initial portfolio value

### Styling (Optional):
Create `.streamlit/config.toml` for custom themes:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## 🚨 Security & Best Practices

### ✅ What's Secure:
- **Public Repository Safe**: No credentials in code
- **Streamlit Secrets**: Encrypted credential storage
- **HTTPS Only**: Automatic SSL/TLS protection  
- **Memory Processing**: No permanent file storage
- **Email Validation**: Only authorized university emails

### 🔐 Security Recommendations:
1. **Strong Passwords**: Use complex class passwords (8+ chars, mixed case, numbers, symbols)
2. **Regular Updates**: Change passwords each semester
3. **Access Reviews**: Periodically review authorized email list
4. **Monitor Usage**: Check Streamlit Cloud analytics for unusual activity

### ⚠️ Important Notes:
- Never commit `.streamlit/secrets.toml` to GitHub (already in .gitignore)
- Excel files with real data are not committed (also in .gitignore)
- All processing happens in memory - no permanent data storage

## 🆘 Troubleshooting

### Authentication Issues:
- **Invalid email/password**: Check spelling and case sensitivity
- **Can't access**: Verify email is in ALLOWED_EMAILS list
- **Secrets not working**: Ensure proper TOML format in Streamlit Cloud

### Deployment Problems:
- **App won't start**: Check Streamlit Cloud logs for specific errors
- **Missing dependencies**: Verify `requirements.txt` is complete
- **File not found**: Ensure `streamlit_app.py` is in repository root

### Data Processing Errors:
- **Excel format**: Ensure files match expected column structure
- **Yahoo Finance**: API may have rate limits or temporary outages
- **Large files**: Check file size limits and processing timeouts

### Getting Help:
1. Check Streamlit Cloud deployment logs
2. Review error messages in dashboard
3. Verify secrets configuration format
4. Test with demo mode if authentication fails

## 🌟 Advantages of This Setup

### For Students & Faculty:
- **Zero Cost**: Free hosting on Streamlit Cloud
- **Easy Access**: Just need university email + password
- **No Setup**: No local installation required
- **Always Updated**: Latest code deployed automatically

### For IT/Security:
- **Public Repository**: No security concerns with code visibility
- **No Server Management**: Fully managed hosting
- **Encrypted Secrets**: Streamlit handles secure credential storage
- **Audit Trail**: Streamlit Cloud provides access logs

### For Development:
- **Easy Updates**: Push to GitHub, auto-deploy
- **Secret Management**: Change credentials without code changes
- **Scalable**: Handles multiple concurrent users
- **Extensible**: Easy to add new features

## 📚 Additional Resources

- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **Secrets Management**: [docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- **GitHub Integration**: [docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)

---

🎉 **Your SMIF dashboard is now ready for secure, public deployment!**